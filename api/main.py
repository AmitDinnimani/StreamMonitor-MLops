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
def predict(request_id: str, data_point: PredictionRequest):
    data_dict = data_point.model_dump() 
    data_array = np.array(list(data_dict.values())) 
    model = load_model() 
    predict = model.predict(data_array.reshape(1, -1)) 
    m_processor.backend_ops(data_dict,predict,request_id)

    return PredictionResponse(
        prediction=prediction,
        request_id=request_id,
        timestamp = datetime.now(timezone.utc).isoformat()
    )
