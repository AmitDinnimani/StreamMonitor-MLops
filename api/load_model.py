import joblib
from functools import lru_cache
from pathlib import Path

ROOT_DIR  = Path(__file__).resolve().parent.parent 

MODEL_PATH = ROOT_DIR / "models/model_v1.pkl"


@lru_cache(maxsize=1)
def get_model():
    """
    Load and cache the ML model.
    This ensures the model is loaded only once.
    """
    model = joblib.load(MODEL_PATH)
    return model
