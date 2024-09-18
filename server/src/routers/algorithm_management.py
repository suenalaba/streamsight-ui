from typing import cast
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from src.db_utils import get_evaluator_stream_from_db, update_evaluator_stream

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

    try:
        evaluator_streamer = get_evaluator_stream_from_db(evaluator_streamer_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")

    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        algorithm_uuid = evaluator_streamer.register_algorithm(algorithm_name=request.algorithm_name)
        update_evaluator_stream(evaluator_streamer_uuid, evaluator_streamer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering algorithm: {str(e)}")

    return {"algorithm_uuid": str(algorithm_uuid)}


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/state")
def get_algorithm_state(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Stream UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Algorithm UUID format")

    try:
        evaluator_streamer = get_evaluator_stream_from_db(evaluator_streamer_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")
    
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting algorithm state: {str(e)}")
    
    return {"algorithm_state": algorithm_state}


@router.get("/streams/{stream_id}/algorithms/state")
def get_all_algorithm_state(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Stream UUID format")
    
    try:
        evaluator_streamer = get_evaluator_stream_from_db(evaluator_streamer_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")

    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    
    try:
        algorithm_states = {key: value.name for key, value in evaluator_streamer.get_all_algorithm_status().items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all algorithm states: {str(e)}")
    
    return {"algorithm_states": algorithm_states}

@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/is-completed")
def is_algorithm_streaming_completed(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Stream UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Algorithm UUID format")
    
    try:
        evaluator_streamer = get_evaluator_stream_from_db(evaluator_streamer_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Stream: {str(e)}")

    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
        return algorithm_state == "COMPLETED"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking if algorithm streaming is completed: {str(e)}")
