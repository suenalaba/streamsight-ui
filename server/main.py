from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel

from streamsight.datasets import (AmazonBookDataset, 
                                  AmazonComputerDataset, 
                                  AmazonMovieDataset, 
                                  AmazonMusicDataset, 
                                  YelpDataset)

from streamsight.settings import SlidingWindowSetting
from streamsight.registries.registry import MetricEntry
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer

from uuid import uuid4

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
