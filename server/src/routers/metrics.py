import json
from typing import cast
from uuid import UUID

from fastapi import APIRouter, HTTPException
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer

from src.db_utils import get_evaluator_stream_from_db, update_evaluator_stream

router = APIRouter(
  tags=["Metrics"],
)

@router.get("/streams/{stream_id}/metrics")
def get_metrics(stream_id: str):
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
        micro_metrics = evaluator_streamer.metric_results("micro")
        macro_metrics = evaluator_streamer.metric_results("macro")

        micro_json = micro_metrics.to_json()
        macro_json = macro_metrics.to_json()

        metrics_dict = {
            "micro_metrics": json.loads(micro_json),
            "macro_metrics": json.loads(macro_json)
        }

        metrics_json = json.dumps(metrics_dict)
        
        update_evaluator_stream(evaluator_streamer_uuid, evaluator_streamer)
        
        return metrics_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Metrics: {str(e)}")
    
