from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_stream_from_db,
    update_stream,
)
from src.utils.string_utils import split_string_by_last_underscore
from src.utils.uuid_utils import InvalidUUIDException, get_stream_uuid_object

router = APIRouter(
    tags=["Metrics"],
)


class MicroMetric(BaseModel):
    algorithm_name: str
    algorithm_id: str
    metric: str
    micro_score: float
    num_user: int


class MacroMetric(BaseModel):
    algorithm_name: str
    algorithm_id: str
    metric: str
    macro_score: float
    num_window: int


class Metrics(BaseModel):
    micro_metrics: list[MicroMetric]
    macro_metrics: list[MacroMetric]


@router.get("/streams/{stream_id}/metrics")
def get_metrics(stream_id: str) -> Metrics:
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        micro_metrics = evaluator_streamer.metric_results("micro")
        macro_metrics = evaluator_streamer.metric_results("macro")

        micro_metrics_dict = micro_metrics.reset_index().to_dict(orient="records")
        macro_metrics_dict = macro_metrics.reset_index().to_dict(orient="records")

        micro_metrics_results: list[MicroMetric] = []
        macro_metrics_results: list[MacroMetric] = []
        for metric in micro_metrics_dict:
            algorithm_name, algorithm_id = split_string_by_last_underscore(
                metric["Algorithm"]
            )
            micro_metrics_results.append(
                MicroMetric(
                    algorithm_name=algorithm_name,
                    algorithm_id=algorithm_id,
                    metric=metric["Metric"],
                    micro_score=metric["micro_score"],
                    num_user=metric["num_user"],
                )
            )
        for metric in macro_metrics_dict:
            algorithm_name, algorithm_id = split_string_by_last_underscore(
                metric["Algorithm"]
            )
            macro_metrics_results.append(
                MacroMetric(
                    algorithm_name=algorithm_name,
                    algorithm_id=algorithm_id,
                    metric=metric["Metric"],
                    macro_score=metric["macro_score"],
                    num_window=metric["num_window"],
                )
            )

        update_stream(evaluator_streamer_uuid, evaluator_streamer)

        return {
            "micro_metrics": micro_metrics_results,
            "macro_metrics": macro_metrics_results,
        }
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Getting Metrics: {str(e)}")
