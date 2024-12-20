from enum import Enum
from typing import List, cast

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from streamsight.datasets import (
    AmazonBookDataset,
    AmazonComputerDataset,
    AmazonMovieDataset,
    AmazonMusicDataset,
    LastFMDataset,
    MovieLens100K,
    TestDataset,
    YelpDataset,
)
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.registries.registry import MetricEntry
from streamsight.settings import SlidingWindowSetting

from src.constants import TEST_USER_ID
from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_stream_from_db,
    get_stream_from_db_with_dataset_id,
    get_user_stream_ids_from_db,
    update_stream,
    update_user_stream_mappings,
    write_stream_to_db,
)
from src.utils.uuid_utils import InvalidUUIDException, get_stream_uuid_object

router = APIRouter(tags=["Stream Management"])

dataset_map = {
    "amazon_music": AmazonMusicDataset,
    "amazon_book": AmazonBookDataset,
    "amazon_computer": AmazonComputerDataset,
    "amazon_movie": AmazonMovieDataset,
    "yelp": YelpDataset,
    "test": TestDataset,
    "movielens": MovieLens100K,
    "lastfm": LastFMDataset,
}


class Metric(str, Enum):
    PrecisionK = "PrecisionK"
    RecallK = "RecallK"
    DCGK = "DCGK"


class Stream(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[Metric]
    background_t: int
    window_size: int
    n_seq_data: int


class StreamStatus(BaseModel):
    stream_id: str
    status: str


@router.post("/streams")
def create_stream(stream: Stream):
    try:
        dataset = dataset_map[stream.dataset_id]()
    except KeyError:
        raise HTTPException(status_code=404, detail="Invalid Dataset ID")

    try:
        data = dataset.load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")

    try:
        setting_sliding = SlidingWindowSetting(
            background_t=stream.background_t,
            window_size=stream.window_size,
            n_seq_data=stream.n_seq_data,
            # background_t=1406851200,
            # window_size=60 * 60 * 24 * 300,  # day times N
            # n_seq_data=3,
            top_K=stream.top_k,
        )
        setting_sliding.split(data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error setting up sliding window: {str(e)}"
        )

    try:
        metrics = []
        for metric in stream.metrics:
            metrics.append(MetricEntry(metric, K=stream.top_k))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating metrics: {str(e)}")

    try:
        evaluator_streamer = EvaluatorStreamer(metrics, setting_sliding, stream.top_k)
        stream_id = write_stream_to_db(evaluator_streamer, stream.dataset_id)
        update_user_stream_mappings(TEST_USER_ID, stream_id)
    except DatabaseErrorException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating evaluator streamer: {str(e)}"
        )

    return {"evaluator_stream_id": stream_id}


@router.get("/streams/{stream_id}/status")
def get_stream_status(stream_id: str):
    try:
        uuid_obj = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(uuid_obj)
        if not evaluator_streamer.has_started:
            return StreamStatus(stream_id=stream_id, status="NOT_STARTED")
        for value in evaluator_streamer.get_all_algorithm_status().values():
            if value.name != "COMPLETED":
                return StreamStatus(stream_id=stream_id, status="IN_PROGRESS")
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    return StreamStatus(stream_id=stream_id, status="COMPLETED")


@router.get("/streams/user")
def get_user_stream_statuses():
    # TODO: Get user-id from header
    stream_statuses: list[StreamStatus] = []
    try:
        stream_uuid_objs = get_user_stream_ids_from_db(TEST_USER_ID)
        for stream_uuid_obj in stream_uuid_objs:
            evaluator_streamer = get_stream_from_db(stream_uuid_obj)
            status = "COMPLETED"
            for value in evaluator_streamer.get_all_algorithm_status().values():
                if value.name != "COMPLETED":
                    status = "IN_PROGRESS"
            if not evaluator_streamer.has_started:
                status = "NOT_STARTED"
            stream_statuses.append(
                StreamStatus(stream_id=str(stream_uuid_obj), status=status)
            )
        return stream_statuses
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/streams/{stream_id}/settings")
def get_stream_settings(stream_id: str):
    try:
        uuid_obj = get_stream_uuid_object(stream_id)
        evaluator_streamer, dataset_id = get_stream_from_db_with_dataset_id(uuid_obj)
        if evaluator_streamer.setting._sliding_window_setting:
            sliding_window_setting = cast(
                SlidingWindowSetting, evaluator_streamer.setting
            )

            n_seq_data = sliding_window_setting.n_seq_data
            window_size = sliding_window_setting.window_size
            background_t = sliding_window_setting.t
            top_k = sliding_window_setting.top_K
            metric_names = [entry.name for entry in evaluator_streamer.metric_entries]

            data = {
                "n_seq_data": n_seq_data,
                "window_size": window_size,
                "background_t": background_t,
                "top_k": top_k,
                "metrics": metric_names,
                "dataset_id": dataset_id,
            }

            json_data = jsonable_encoder(data)

            return JSONResponse(content=json_data)
        else:
            raise HTTPException(
                status_code=501, detail="Other settings are currently not supported"
            )
    except HTTPException:
        raise
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/streams/{stream_id}/start")
def start_stream(stream_id: str):
    try:
        uuid_obj = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(uuid_obj)
        evaluator_streamer.start_stream()
        update_stream(uuid_obj, evaluator_streamer)
        return {"status": True}
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=f"Error Starting Stream: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Starting Stream: {str(e)}")
