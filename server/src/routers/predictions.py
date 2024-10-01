from typing import List, Union

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from scipy.sparse import csr_matrix
from streamsight.matrix import InteractionMatrix

from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_stream_from_db,
    update_stream,
)
from src.utils.uuid_utils import (
    InvalidUUIDException,
    get_algo_uuid_object,
    get_stream_uuid_object,
)

router = APIRouter(tags=["Predictions"])


class PredictionCsrMatrix(BaseModel):
    data: List[float]
    indices: List[int]
    indptr: List[int]
    shape: List[int]


class DataframeRecord(BaseModel):
    interactionid: int = Field(..., description="The ID of the interaction, required.")
    uid: int = Field(..., description="The user ID, required.")
    iid: int = Field(..., description="The item ID, required.")
    ts: int = Field(..., description="The timestamp of the interaction, required.")


@router.post("/streams/{stream_id}/algorithms/{algorithm_id}/predictions")
async def submit_prediction(
    stream_id: str,
    algorithm_id: str,
    predictions: Union[List[DataframeRecord], PredictionCsrMatrix],
):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        if isinstance(predictions, list) and all(
            isinstance(prediction, DataframeRecord) for prediction in predictions
        ):
            prediction_data = [prediction.model_dump() for prediction in predictions]
            prediction_df = pd.DataFrame(prediction_data)
            prediction_im = InteractionMatrix(
                prediction_df, item_ix="iid", user_ix="uid", timestamp_ix="ts"
            )

            evaluator_streamer.submit_prediction(algorithm_uuid, prediction_im)
            assert evaluator_streamer.get_algorithm_state(algorithm_uuid).name in {
                "PREDICTED",
                "COMPLETED",
            }
        elif isinstance(predictions, PredictionCsrMatrix):
            prediction_csr_matrix = csr_matrix(
                (predictions.data, predictions.indices, predictions.indptr),
                shape=predictions.shape,
            )
            evaluator_streamer.submit_prediction(algorithm_uuid, prediction_csr_matrix)
            assert evaluator_streamer.get_algorithm_state(algorithm_uuid).name in {
                "PREDICTED",
                "COMPLETED",
            }
        update_stream(evaluator_streamer_uuid, evaluator_streamer)
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error Submitting Prediction: {str(e)}"
        )

    return {"status": True}
