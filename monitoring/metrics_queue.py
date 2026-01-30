from collections import deque
from datetime import datetime, timezone
import pandas as pd

STREAM_BUFFER = deque(maxlen=10000)


def add_in_buffer(buffer,features: dict, prediction: float, req_id: str):
    buffer.append({
        "timestamp": datetime.now(timezone.utc),
        "req_id": req_id,
        "features": features,
        "prediction": prediction
    })
    print('data appended in buffer')


def get_features_df(buffer) -> pd.DataFrame:
    recent_items = list(buffer)
    features_list = [item["features"] for item in recent_items]

    return pd.DataFrame(features_list)
