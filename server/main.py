import io
from typing import List, Optional, Union, cast

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from streamsight.datasets import (AmazonBookDataset, 
                                  AmazonComputerDataset, 
                                  AmazonMovieDataset, 
                                  AmazonMusicDataset, 
                                  YelpDataset)

from streamsight.settings import SlidingWindowSetting
from streamsight.registries.registry import MetricEntry
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer

from uuid import UUID, uuid4
import pandas as pd

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class Stream(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[str]

dataset_map = {
    'amazon_music': AmazonMusicDataset,
    'amazon_book': AmazonBookDataset,
    'amazon_computer': AmazonComputerDataset,
    'amazon_movie': AmazonMovieDataset,
    'yelp': YelpDataset
}

# stores k:v pair of UUID: EvaluatorStreamer
evaluator_stream_object_map = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.post("/create-stream")
def create_stream(stream: Stream):
    dataset = dataset_map[stream.dataset_id]()
    data = dataset.load()

    setting_sliding = SlidingWindowSetting(
        background_t=1406851200,
        window_size=60 * 60 * 24 * 300, # day times N
        n_seq_data=3,
        top_K=stream.top_k,
    )
    setting_sliding.split(data)

    metrics = []
    for metric in stream.metrics:
        metrics.append(MetricEntry(metric, K=stream.top_k))

    evaluator_streamer = EvaluatorStreamer(metrics, setting_sliding)
    evaluator_streamer_id = uuid4()
    evaluator_stream_object_map[evaluator_streamer_id] = evaluator_streamer

    return evaluator_streamer_id


@app.get("/get_stream/{evaluator_streamer_id}")
def get_stream(evaluator_streamer_id: str):
    try:
        uuid_obj = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer = evaluator_stream_object_map.get(uuid_obj)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    return evaluator_streamer


class AlgorithmRegistrationRequest(BaseModel):
    algorithm_name: str

@app.post("/register_algorithm/{evaluator_streamer_id}")
def register_algorithm(evaluator_streamer_id: str, request: AlgorithmRegistrationRequest):

    try:
        evaluator_streamer_uuid = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_uuid = evaluator_streamer.register_algorithm(algorithm_name=request.algorithm_name)

    return {"algorithm_uuid": str(algorithm_uuid)}


@app.get("/get_algorithm_state/{evaluator_streamer_id}/{algorithm_id}")
def get_algorithm_state(evaluator_streamer_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
    return {"algorithm_state": algorithm_state}


@app.get("/get_algorithm_state/{evaluator_streamer_id}")
def get_all_algorithm_state(evaluator_streamer_id: str):
    try:
        evaluator_streamer_uuid = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_states = {key: value.name for key, value in evaluator_streamer.get_all_algorithm_status().items()}
    return {"algorithm_states": algorithm_states}


@app.post("/start_stream/{evaluator_streamer_id}")
def start_stream(evaluator_streamer_id: str):
    try:
        evaluator_streamer_uuid = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        evaluator_streamer.start_stream()
        return {"status": True}
    except Exception as e:
        return {"status": False, "error": f"Error Starting Stream: {str(e)}"}


@app.get("/get_data/{evaluator_streamer_id}/{algorithm_id}")
def download_data(evaluator_streamer_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(evaluator_streamer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    interaction_matrix = evaluator_streamer.get_data(algorithm_uuid)
    df = interaction_matrix.copy_df()

    algo_name = evaluator_streamer.status_registry.get(algorithm_uuid).name
    file_name = f"{algo_name}.csv"

    # Convert DataFrame to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(csv_buffer, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={file_name}"})