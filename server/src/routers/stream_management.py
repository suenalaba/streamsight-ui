from enum import Enum
from typing import List, Optional, cast
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from streamsight.datasets import (AmazonBookDataset, 
                                  AmazonComputerDataset, 
                                  AmazonMovieDataset, 
                                  AmazonMusicDataset, 
                                  YelpDataset)
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.settings import SlidingWindowSetting
from streamsight.registries.registry import MetricEntry
from src.constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Stream Management"]
)

dataset_map = {
    'amazon_music': AmazonMusicDataset,
    'amazon_book': AmazonBookDataset,
    'amazon_computer': AmazonComputerDataset,
    'amazon_movie': AmazonMovieDataset,
    'yelp': YelpDataset
}

class Metric(str, Enum):
    PrecisionK = "PrecisionK"
    RecallK = "RecallK"
    DCGK = "DCGK"

class Stream(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[Metric]

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
            background_t=1406851200,
            window_size=60 * 60 * 24 * 300,  # day times N
            n_seq_data=3,
            top_K=stream.top_k,
        )
        setting_sliding.split(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up sliding window: {str(e)}")

    try:
        metrics = []
        for metric in stream.metrics:
            metrics.append(MetricEntry(metric, K=stream.top_k))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating metrics: {str(e)}")

    try:
        evaluator_streamer = EvaluatorStreamer(metrics, setting_sliding, stream.top_k)
        stream_id = uuid4()
        evaluator_stream_object_map[stream_id] = evaluator_streamer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating evaluator streamer: {str(e)}")

    return {"evaluator_stream_id": stream_id}


@router.get("/streams/{stream_id}")
def get_stream(stream_id: str):
    try:
        uuid_obj = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer = evaluator_stream_object_map.get(uuid_obj)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    return evaluator_streamer


@router.post("/streams/{stream_id}/start")
def start_stream(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        evaluator_streamer.start_stream()
        return {"status": True}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=f"Error Starting Stream: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Starting Stream: {str(e)}")
