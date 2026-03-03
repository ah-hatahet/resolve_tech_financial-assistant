import joblib
import numpy as np
import json
import os


def model_fn(model_dir):
    """Load the model from the model directory."""
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model


def input_fn(request_body, content_type="application/json"):
    """Parse the incoming request."""
    if content_type == "application/json":
        data = json.loads(request_body)
        # Expects: {"features": [MedInc, HouseAge, AveRooms, AveBedrms,
        #                         Population, AveOccup, Latitude, Longitude]}
        return np.array(data["features"]).reshape(1, -1)
    raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model):
    """Run prediction."""
    return model.predict(input_data)


def output_fn(prediction, accept="application/json"):
    """Format the response as a plain JSON string."""
    return json.dumps({"predicted_value": float(prediction[0])}), "application/json"