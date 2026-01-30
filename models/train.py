import json
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

data = fetch_california_housing(as_frame=True)

X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
rmse = mean_squared_error(y_test, preds)
print(f"Model trained: MAE={mae:.4f}, RMSE={rmse:.4f}")

joblib.dump(model, "models/model_v1.pkl")

metadata = {
    "features": list(X.columns),
    "target": "MedHouseValue",
    "MAE": mae,
    "RMSE": rmse
}
with open("models/metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)