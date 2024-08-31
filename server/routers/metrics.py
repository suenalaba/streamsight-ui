import json
from typing import Optional, cast
from uuid import UUID
from fastapi import APIRouter, HTTPException
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Metrics"],
)

@router.get("/streams/{stream_id}/metrics")
def get_metrics(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        micro_metrics = evaluator_streamer.metric_results("micro")
        macro_metrics = evaluator_streamer.metric_results("macro")

        micro_json = micro_metrics.to_json()
        macro_json = macro_metrics.to_json()

        # Combine both JSON strings into a dictionary
        metrics_dict = {
            "micro_metrics": json.loads(micro_json),
            "macro_metrics": json.loads(macro_json)
        }

        # Convert the dictionary to a JSON string to send to the frontend
        metrics_json = json.dumps(metrics_dict)
        return metrics_json
    except Exception as e:
        return {"status": False, "error": f"Error Getting Metrics: {str(e)}"}