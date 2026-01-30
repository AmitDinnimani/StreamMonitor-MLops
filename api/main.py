import numpy as np
from datetime import datetime,timezone
from fastapi import FastAPI

from api.schemas import PredictionRequest, PredictionResponse
from api.load_model import get_model
from monitoring.processor import MetricsProcessor


app = FastAPI(title="StreamMonitor API")
model = get_model()

m_processor  = MetricsProcessor(drift_threshold=0.3,global_threshold=0.3)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict/{request_id}", response_model=PredictionResponse)
def predict(request_id: str, data_point: PredictionRequest):
    data_dict = data_point.model_dump() 
    data_array = np.array(list(data_dict.values())) 
    
    predict = model.predict(data_array.reshape(1, -1)) 
    m_processor.backend_ops(data_dict,predict[0],request_id)

    return PredictionResponse(
        prediction=predict[0],
        request_id=request_id,
        timestamp = datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True,log_level="info")