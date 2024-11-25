from typing import List, Union

from fastapi import APIRouter, HTTPException, Query

from src.models.metadata import (
    AmazonMovieItem,
    LastFM2kItem,
    LastFM2kTag,
    LastFM2kUser,
    MovieLens100kItem,
    MovieLens100kUser,
)
from src.utils.db_utils import (
    DatabaseErrorException,
    GetEvaluatorStreamErrorException,
    get_metadata_from_db,
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
def get_training_data(
    stream_id: str,
    algorithm_id: str,
    includeAdditionalFeatures: bool = Query(
        False, description="Include additional features in the training data"
    ),
):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        interaction_matrix = evaluator_streamer.get_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        main_columns = ["interactionid", "uid", "iid", "ts"]
        if includeAdditionalFeatures:
            df_json = df.to_dict(orient="records")
        else:
            # only include the main columns if user does not want additional features
            df_json = df[main_columns].to_dict(orient="records")
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
def get_unlabeled_data(
    stream_id: str,
    algorithm_id: str,
    includeAdditionalFeatures: bool = Query(
        False, description="Include additional features in the unlabeled data"
    ),
):
    try:
        evaluator_streamer_uuid = get_stream_uuid_object(stream_id)
        algorithm_uuid = get_algo_uuid_object(algorithm_id)
        evaluator_streamer = get_stream_from_db(evaluator_streamer_uuid)
        interaction_matrix = evaluator_streamer.get_unlabeled_data(algorithm_uuid)
        shape = interaction_matrix.shape
        df = interaction_matrix.copy_df()
        main_columns = ["interactionid", "uid", "iid", "ts"]
        if includeAdditionalFeatures:
            df_json = df.to_dict(orient="records")
        else:
            # only include the main columns if user does not want additional features
            df_json = df[main_columns].to_dict(orient="records")
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


metadata_mappings = {
    "amazon_movie_item": AmazonMovieItem,
    "movielens100k_user": MovieLens100kUser,
    "movielens100k_item": MovieLens100kItem,
    "lastfm2k_user": LastFM2kUser,
    "lastfm2k_item": LastFM2kItem,
    "lastfm2k_tag": LastFM2kTag,
}


@router.get(
    "/metadata/{metadata_id}",
    response_model=List[Union[tuple(metadata_mappings.values())]],
)
def get_metadata(metadata_id: str):
    if metadata_id not in metadata_mappings:
        raise HTTPException(
            status_code=404, detail=f"Metadata with ID {metadata_id} not found"
        )
    try:
        metadatas = get_metadata_from_db(metadata_mappings[metadata_id])
        return metadatas
    except DatabaseErrorException as e:
        raise HTTPException(
            status_code=e.status_code, detail=f"Metadata ID: {metadata_id}, {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting metadata with ID {metadata_id}: {str(e)}",
        )
