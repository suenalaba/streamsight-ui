from fastapi import APIRouter, HTTPException

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

router = APIRouter(tags=["Data Handling"])


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/training-data")
def get_training_data(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        interaction_matrix = evaluator_streamer.get_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        df_json = df.to_dict(orient="records")
        update_stream(evaluator_streamer_uuid, evaluator_streamer)
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error Getting Training Data: " + str(e)
        )

    return {"shape": shape, "training_data": df_json}


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/unlabeled-data")
def get_unlabeled_data(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        interaction_matrix = evaluator_streamer.get_unlabeled_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        df_json = df.to_dict(orient="records")
        update_stream(evaluator_streamer_uuid, evaluator_streamer)
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error Getting Unlabeled Data: {str(e)}"
        )

    return {"shape": shape, "unlabeled_data": df_json}
