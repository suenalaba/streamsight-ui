from enum import Enum
from typing import List

from pydantic import BaseModel


class Metric(str, Enum):
    PrecisionK = "PrecisionK"
    RecallK = "RecallK"
    DCGK = "DCGK"
    NDCGK = "NDCGK"
    HITK = "HitK"


class Stream(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[Metric]
    background_t: int
    window_size: int
    n_seq_data: int


class StreamStatusEnum(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class StreamStatus(BaseModel):
    stream_id: str
    status: StreamStatusEnum


class CreateStreamResponse(BaseModel):
    evaluator_stream_id: str


class StreamSettings(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[str]
    background_t: int
    window_size: int
    n_seq_data: int
    number_of_windows: int
    current_window: int


class StartStreamResponse(BaseModel):
    status: bool
