from fastapi import APIRouter, HTTPException

from src.models.algorithm_management_models import (
    AlgorithmRegistrationRequest,
    GetAlgorithmStateResponse,
    GetAllAlgorithmStateResponse,
    RegisterAlgorithmResponse,
)
from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_stream_from_db,
    update_stream,
)
from src.utils.string_utils import split_string_by_last_underscore
from src.utils.uuid_utils import (
    InvalidUUIDException,
    get_algo_uuid_object,
    get_stream_uuid_object,
)

router = APIRouter(tags=["Algorithm Management"])


@router.post("/streams/{stream_id}/algorithms")
def register_algorithm(
    stream_id: str, request: AlgorithmRegistrationRequest
) -> RegisterAlgorithmResponse:
    try:
        uuid_obj = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(uuid_obj)
        algorithm_uuid = evaluator_streamer.register_algorithm(
            algorithm_name=request.algorithm_name
        )
        update_stream(uuid_obj, evaluator_streamer)
    except (
        InvalidUUIDException,
        GetEvaluatorStreamErrorException,
        DatabaseErrorException,
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error registering algorithm: " + str(e)
        )

    return {"algorithm_uuid": str(algorithm_uuid)}


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/state")
def get_algorithm_state(stream_id: str, algorithm_id: str) -> GetAlgorithmStateResponse:
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error getting algorithm state: " + str(e)
        )

    return {"algorithm_state": algorithm_state}


@router.get("/streams/{stream_id}/algorithms/state")
def get_all_algorithm_state(stream_id: str) -> GetAllAlgorithmStateResponse:
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        algorithm_states = [
            {
                "algorithm_uuid": split_string_by_last_underscore(key)[1],
                "algorithm_name": split_string_by_last_underscore(key)[0],
                "state": value.name,
            }
            for key, value in evaluator_streamer.get_all_algorithm_status().items()
        ]
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting all algorithm states: {str(e)}"
        )

    return algorithm_states


@router.get("/streams/{stream_id}/algorithms/{algorithm_id}/is-completed")
def is_algorithm_streaming_completed(stream_id: str, algorithm_id: str) -> bool:
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
        return algorithm_state == "COMPLETED"
    except (InvalidUUIDException, GetEvaluatorStreamErrorException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error checking if algorithm streaming is completed: " + str(e),
        )
