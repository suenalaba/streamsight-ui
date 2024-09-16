import io
from typing import Optional, cast
from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from src.constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Data Handling"]
)

@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/training-data")
def get_training_data(stream_id: str, algorithm_id: str):
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
    
    try:
        interaction_matrix = evaluator_streamer.get_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        df_json = df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Training Data: {str(e)}")

    return {"shape": shape, "training_data": df_json}


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/unlabeled-data")
def get_unlabeled_data(stream_id: str, algorithm_id: str):
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
    
    try:
        interaction_matrix = evaluator_streamer.get_unlabeled_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        df_json = df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Training Data: {str(e)}")

    return {"shape": shape, "unlabeled_data": df_json}
