from typing import Optional, cast
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from src.constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Algorithm Management"]
)

class AlgorithmRegistrationRequest(BaseModel):
    algorithm_name: str

@router.post("/streams/{stream_id}/algorithms")
def register_algorithm(stream_id: str, request: AlgorithmRegistrationRequest):

    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_uuid = evaluator_streamer.register_algorithm(algorithm_name=request.algorithm_name)

    return {"algorithm_uuid": str(algorithm_uuid)}


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/state")
def get_algorithm_state(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
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


@router.get("/streams/{stream_id}/algorithms/state")
def get_all_algorithm_state(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_states = {key: value.name for key, value in evaluator_streamer.get_all_algorithm_status().items()}
    return {"algorithm_states": algorithm_states}

