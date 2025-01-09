import pickle
import uuid
from typing import Tuple

from sqlmodel import Session, SQLModel, select
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer

from src.database import EvaluatorStreamModel, get_sql_connection


class GetEvaluatorStreamErrorException(Exception):
    def __init__(
        self, message="Error getting evaluator stream from database", status_code=500
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseErrorException(Exception):
    def __init__(self, message="Database CRUD Error", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def get_stream_from_db(stream_id: uuid.UUID) -> EvaluatorStreamer:
    try:
        with Session(get_sql_connection()) as session:
            evaluator_stream = session.get(EvaluatorStreamModel, stream_id)
            if not evaluator_stream:
                raise GetEvaluatorStreamErrorException(
                    message=f"Evaluator stream with ID {stream_id} not found",
                    status_code=404,
                )
            eval_streamer: EvaluatorStreamer = pickle.loads(
                evaluator_stream.stream_object
            )
            eval_streamer.restore()
            return eval_streamer
    except GetEvaluatorStreamErrorException as e:
        raise e
    except Exception as e:
        raise GetEvaluatorStreamErrorException(
            message="Error getting evaluator stream from database: " + str(e)
        )


def get_stream_from_db_with_dataset_id(
    stream_id: uuid.UUID,
) -> Tuple[EvaluatorStreamer, str]:
    try:
        with Session(get_sql_connection()) as session:
            evaluator_stream = session.get(EvaluatorStreamModel, stream_id)
            if not evaluator_stream:
                raise GetEvaluatorStreamErrorException(
                    message=f"Evaluator stream with ID {stream_id} not found",
                    status_code=404,
                )
            eval_streamer: EvaluatorStreamer = pickle.loads(
                evaluator_stream.stream_object
            )
            eval_streamer.restore()
            return eval_streamer, evaluator_stream.dataset_id
    except GetEvaluatorStreamErrorException as e:
        raise e
    except Exception as e:
        raise GetEvaluatorStreamErrorException(
            message="Error getting evaluator stream from database: " + str(e)
        )


def is_user_stream(stream_id: uuid.UUID, user_id: str) -> bool:
    try:
        with Session(get_sql_connection()) as session:
            statement = select(EvaluatorStreamModel).where(
                EvaluatorStreamModel.stream_id == stream_id
            ).where(EvaluatorStreamModel.user_id == user_id)
            results = session.exec(statement)
            stream = results.first()
            if not stream:
                return False
            return True
    except GetEvaluatorStreamErrorException as e:
        raise e
    except Exception as e:
        raise GetEvaluatorStreamErrorException(
            message="Error getting evaluator stream from database: " + str(e)
        )


def update_stream(stream_id: uuid.UUID, evaluator_streamer: EvaluatorStreamer):
    try:
        with Session(get_sql_connection()) as session:
            statement = select(EvaluatorStreamModel).where(
                EvaluatorStreamModel.stream_id == stream_id
            )
            results = session.exec(statement)
            stream = results.first()

            evaluator_streamer.prepare_dump()
            stream.stream_object = pickle.dumps(evaluator_streamer)

            session.add(stream)
            session.commit()
            session.refresh(stream)
    except Exception as e:
        raise DatabaseErrorException(
            "Error updating evaluator stream in database: " + str(e)
        )


def write_stream_to_db(evaluator_streamer: EvaluatorStreamer, dataset_id: str, user_id: str):
    try:
        evaluator_streamer.prepare_dump()
        evaluator_stream_obj = pickle.dumps(evaluator_streamer)

        with Session(get_sql_connection()) as session:
            new_stream = EvaluatorStreamModel(
                stream_object=evaluator_stream_obj, 
                dataset_id=dataset_id,
                user_id=uuid.UUID(user_id),
            )
            session.add(new_stream)
            session.commit()
            return new_stream.stream_id
    except Exception as e:
        raise DatabaseErrorException(
            "Error write evaluator stream to database: " + str(e)
        )


def get_metadata_from_db(metadata_model: SQLModel) -> list[SQLModel]:
    try:
        with Session(get_sql_connection()) as session:
            statement = select(metadata_model)
            query_results = session.exec(statement)
            metadata = query_results.all()
            return metadata
    except Exception as e:
        raise DatabaseErrorException("Error getting metadata from database: " + str(e))


def get_user_stream_ids_from_db(user_id: str) -> list[uuid.UUID]:
    try:
        with Session(get_sql_connection()) as session:
            statement = select(EvaluatorStreamModel).where(
                EvaluatorStreamModel.user_id == user_id
            )
            query_results = session.exec(statement)
            results = query_results.all()
            return [result.stream_id for result in results]
    except Exception as e:
        raise DatabaseErrorException(
            "Error getting user stream IDs from database: " + str(e)
        )

