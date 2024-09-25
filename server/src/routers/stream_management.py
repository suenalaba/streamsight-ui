from enum import Enum
from typing import List, cast
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from streamsight.datasets import (
    AmazonBookDataset,
    AmazonComputerDataset,
    AmazonMovieDataset,
    AmazonMusicDataset,
    TestDataset,
    YelpDataset,
)
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.registries.registry import MetricEntry
from streamsight.settings import SlidingWindowSetting

from src.db_utils import (
    get_evaluator_stream_from_db,
    update_evaluator_stream,
    write_evaluator_stream_to_db,
)
from src.utils.db_utils import GetEvaluatorStreamErrorException, get_stream_from_db
from src.utils.uuid_utils import InvalidUUIDException, get_stream_uuid_object

router = APIRouter(tags=["Stream Management"])

dataset_map = {
    "amazon_music": AmazonMusicDataset,
    "amazon_book": AmazonBookDataset,
    "amazon_computer": AmazonComputerDataset,
    "amazon_movie": AmazonMovieDataset,
    "yelp": YelpDataset,
    "test": TestDataset,
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
        stream_id = write_evaluator_stream_to_db(evaluator_streamer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating evaluator streamer: {str(e)}"
        )

    return {"evaluator_stream_id": stream_id}


@router.get("/streams/{stream_id}")
def get_stream(stream_id: str):
    try:
        uuid_obj = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    try:
        evaluator_streamer = get_evaluator_stream_from_db(uuid_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")

    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    return evaluator_streamer.metric_k


@router.get("/streams/{stream_id}/settings")
def get_stream_settings(stream_id: str):
    try:
        uuid_obj = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(uuid_obj)
        if evaluator_streamer.setting._sliding_window_setting:
            sliding_window_setting = cast(
                SlidingWindowSetting, evaluator_streamer.setting
            )

            n_seq_data = sliding_window_setting.n_seq_data
            window_size = sliding_window_setting.window_size
            background_t = sliding_window_setting.t
            top_k = sliding_window_setting.top_K

            data = {
                "n_seq_data": n_seq_data,
                "window_size": window_size,
                "background_t": background_t,
                "top_k": top_k,
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
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    try:
        evaluator_streamer = get_evaluator_stream_from_db(evaluator_streamer_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        evaluator_streamer.start_stream()
        update_evaluator_stream(evaluator_streamer_uuid, evaluator_streamer)
        return {"status": True}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=f"Error Starting Stream: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Starting Stream: {str(e)}")
