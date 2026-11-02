import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from data import load_data, split_data

# Path to the model file, built from this file's location so it works from any folder
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "iris_model.pkl")


def fit_model(X_train, y_train):
    """Train a Random Forest classifier on the training data."""
    model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=12)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Check how accurate the model is on data it has never seen."""
    y_pred = model.predict(X_test)
    return accuracy_score(y_test, y_pred)


if __name__ == "__main__":
    X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)

    model = fit_model(X_train, y_train)
    accuracy = evaluate_model(model, X_test, y_test)
    print(f"Test accuracy: {accuracy:.2%}")

    # Save the model together with information about it
    model_bundle = {
        "model": model,
        "model_type": "RandomForestClassifier",
        "test_accuracy": round(accuracy, 4),
    }
    joblib.dump(model_bundle, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")