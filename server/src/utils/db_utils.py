import pickle
import uuid

from sqlmodel import Session
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer

from src.database import EvaluatorStreamModel, get_sql_connection


class GetEvaluatorStreamErrorException(Exception):
    def __init__(
        self, message="Error getting evaluator stream from database", status_code=500
    ):
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
