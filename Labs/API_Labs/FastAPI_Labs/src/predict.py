import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "iris_model.pkl")

# Names of the 3 iris species, in the same order as the model's class numbers 0, 1, 2
SPECIES_NAMES = ["setosa", "versicolor", "virginica"]

# Load the model once, when the API starts, instead of on every request
model_bundle = joblib.load(MODEL_PATH)
model = model_bundle["model"]


def predict_data(X):
    """
    Predict the species for one flower.
    Returns the class number, species name, and how confident the model is.
    """
    class_id = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    confidence = float(probabilities[class_id])
    return {
        "class_id": class_id,
        "species": SPECIES_NAMES[class_id],
        "confidence": round(confidence, 4),
    }


def get_model_info():
    """Return information about the loaded model."""
    return {
        "model_type": model_bundle["model_type"],
        "test_accuracy": model_bundle["test_accuracy"],
        "species": SPECIES_NAMES,
    }