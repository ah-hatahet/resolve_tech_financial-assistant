import joblib
import pandas as pd
import json
import os


def model_fn(model_dir):
    """Load the model from the model directory."""
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model


def input_fn(request_body, content_type="application/json"):
    """Parse the incoming request into a DataFrame."""
    if content_type == "application/json":
        data = json.loads(request_body)
        # Expects a dict of feature name -> value
        return pd.DataFrame([data])
    raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model):
    """Run prediction and return label + probability."""
    prediction  = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    return {"prediction": int(prediction), "probability": float(probability)}


def output_fn(prediction, accept="application/json"):
    """Format the response."""
    return json.dumps(prediction), "application/json"