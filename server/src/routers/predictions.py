import io
from typing import List, Optional, cast
from uuid import UUID
from fastapi import APIRouter, File, HTTPException, UploadFile
import pandas as pd
from pydantic import BaseModel, Field
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.algorithms import ItemKNNStatic
from streamsight.matrix import InteractionMatrix
from src.constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Predictions"]
)

class DataframeRecord(BaseModel):
    interactionid: int = Field(..., description="The ID of the interaction, required.")
    uid: int = Field(..., description="The user ID, required.")
    iid: int = Field(..., description="The item ID, required.")
    ts: int = Field(..., description="The timestamp of the interaction, required.")

@router.post("/streams/{stream_id}/algorithms/{algorithm_id}/predictions")
async def submit_prediction(stream_id: str, algorithm_id: str, records: List[DataframeRecord]):
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
        prediction_data = [record.model_dump() for record in records]
        prediction_df = pd.DataFrame(prediction_data)
        prediction_im = InteractionMatrix(prediction_df)
        evaluator_streamer.submit_prediction(algorithm_uuid, prediction_im)
        assert evaluator_streamer.get_algorithm_state(algorithm_uuid).name == "PREDICTED"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Submitting Prediction: {str(e)}")
    
    return {"status": True}
