from pydantic import BaseModel
from streamsight.registries import AlgorithmStateEnum


class AlgorithmRegistrationRequest(BaseModel):
    algorithm_name: str


class RegisterAlgorithmResponse(BaseModel):
    algorithm_uuid: str


class GetAlgorithmStateResponse(BaseModel):
    algorithm_state: AlgorithmStateEnum


class AlgorithmState(BaseModel):
    algorithm_uuid: str
    algorithm_name: str
    state: AlgorithmStateEnum


class GetAllAlgorithmStateResponse(BaseModel):
    algorithm_states: list[AlgorithmState]
