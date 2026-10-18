from pydantic import BaseModel


class MoveRequest(BaseModel):
    x: float
    y: float


class RecoveryRequest(BaseModel):
    elapsed_time: float = 0.0
