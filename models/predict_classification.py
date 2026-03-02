import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/logistic_regression_model.pkl")

def predict_subscription(input_data: dict):
    """
    input_data must be a dictionary
    with the same feature names as training data
    """

    df = pd.DataFrame([input_data])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    return prediction, probability


if __name__ == "__main__":
    # Example sample input
    sample_input = {
        "age": 35,
        "job": "management",
        "marital": "married",
        "education": "tertiary",
        "default": "no",
        "balance": 1500,
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "day": 15,
        "month": "may",
        "duration": 200,
        "campaign": 1,
        "pdays": -1,
        "previous": 0,
        "poutcome": "unknown"
    }

    pred, prob = predict_subscription(sample_input)

    print("Prediction (1=Yes, 0=No):", pred)
    print("Probability of Subscription:", prob)