import joblib
import numpy as np

# Load trained model
model = joblib.load("models/random_forest_regressor.pkl")

def predict_house_value(features):
    """
    features must be a list in this order:
    [MedInc, HouseAge, AveRooms, AveBedrms,
     Population, AveOccup, Latitude, Longitude]
    """

    features_array = np.array(features).reshape(1, -1)
    prediction = model.predict(features_array)

    return prediction[0]


if __name__ == "__main__":
    # Example input (sample from dataset scale)
    sample_features = [8.3252, 41, 6.984, 1.023,
                       322, 2.555, 37.88, -122.23]

    result = predict_house_value(sample_features)

    print("Predicted Median House Value:", result)