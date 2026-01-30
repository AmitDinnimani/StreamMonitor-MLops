import numpy as np
from datetime import datetime,timezone
from fastapi import FastAPI

from api.schemas import PredictionRequest, PredictionResponse
from api.load_model import get_model

app = FastAPI(title="StreamMonitor API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict/{request_id}", response_model=PredictionResponse)
def predict(request_id: str, request: PredictionRequest):
    model = get_model()

    data = request.model_dump()
    values = list(data.values())

    X = np.array(values, dtype=float).reshape(1, -1)

    prediction = float(model.predict(X)[0])

    return PredictionResponse(
        prediction=prediction,
        request_id=request_id,
        timestamp = datetime.now(timezone.utc).isoformat()
    )
