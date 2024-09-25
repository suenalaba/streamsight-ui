from uuid import UUID


class InvalidUUIDException(Exception):
    def __init__(self, message="Invalid UUID format", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def get_uuid_object(uuid_str: str, error_message: str):
    try:
        uuid_obj = UUID(uuid_str)
        return uuid_obj
    except ValueError:
        raise InvalidUUIDException(message=error_message)


def get_algo_uuid_object(algo_id: str):
    return get_uuid_object(algo_id, "Invalid Algorithm UUID format")


def get_stream_uuid_object(stream_id: str):
    return get_uuid_object(stream_id, "Invalid Stream UUID format")
