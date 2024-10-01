import json

from fastapi import APIRouter, HTTPException

from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_stream_from_db,
    update_stream,
)
from src.utils.uuid_utils import InvalidUUIDException, get_stream_uuid_object

router = APIRouter(
    tags=["Metrics"],
)


@router.get("/streams/{stream_id}/metrics")
def get_metrics(stream_id: str):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        micro_metrics = evaluator_streamer.metric_results("micro")
        macro_metrics = evaluator_streamer.metric_results("macro")

        micro_json = micro_metrics.to_json()
        macro_json = macro_metrics.to_json()

        metrics_dict = {
            "micro_metrics": json.loads(micro_json),
            "macro_metrics": json.loads(macro_json),
        }

        metrics_json = json.dumps(metrics_dict)

        update_stream(evaluator_streamer_uuid, evaluator_streamer)

        return metrics_json
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Metrics: {str(e)}")
