from pydantic import BaseModel
from datetime import datetime


class PredictionRequest(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    feature4: float
    feature5: float
    feature6: float
    feature7: float
    feature8: float


class PredictionResponse(BaseModel):
    prediction: float
    request_id: str
    timestamp: datetime
