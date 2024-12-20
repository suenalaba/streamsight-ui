from pydantic import BaseModel


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
