import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from kneed import KneeLocator
import pickle
import os
import base64

REQUIRED_COLUMNS = ["BALANCE", "PURCHASES", "CREDIT_LIMIT"]


def validate_data():
    """
    Checks the input CSV before the pipeline uses it.
    Fails the task (and stops the pipeline) if the data is unusable.
    """
    path = os.path.join(os.path.dirname(__file__), "../data/file.csv")

    # Check 1: does the file exist?
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)

    # Check 2: does it have any rows?
    if df.empty:
        raise ValueError("Data file is empty")

    # Check 3: are the columns we need actually there?
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    print(f"Validation passed: {len(df)} rows, all required columns present")


def load_data():
    """
    Loads data from a CSV file, serializes it, and returns the serialized data.
    Returns:
        str: Base64-encoded serialized data (JSON-safe).
    """
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/file.csv"))
    print(f"Loaded {len(df)} rows")
    serialized_data = pickle.dumps(df)                    # bytes
    return base64.b64encode(serialized_data).decode("ascii")  # JSON-safe string


def data_preprocessing(data_b64: str):
    """
    Deserializes base64-encoded pickled data, cleans and scales it,
    saves the fitted scaler, and returns base64-encoded pickled scaled data.
    """
    # decode -> bytes -> DataFrame
    data_bytes = base64.b64decode(data_b64)
    df = pickle.loads(data_bytes)

    df = df.dropna()
    clustering_data = df[REQUIRED_COLUMNS]

    min_max_scaler = MinMaxScaler()
    clustering_data_minmax = min_max_scaler.fit_transform(clustering_data)

    # Save the fitted scaler so the test data can be scaled the same way later
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(min_max_scaler, f)

    # bytes -> base64 string for XCom
    clustering_serialized_data = pickle.dumps(clustering_data_minmax)
    return base64.b64encode(clustering_serialized_data).decode("ascii")


def build_save_model(data_b64: str, filename: str):
    """
    Tries K-Means with k = 1 to 49, uses the elbow method to pick the best k,
    then trains and saves a final model with that k.
    Returns the SSE list (JSON-serializable).
    """
    # decode -> bytes -> numpy array
    data_bytes = base64.b64decode(data_b64)
    df = pickle.loads(data_bytes)

    kmeans_kwargs = {"init": "random", "n_init": 10, "max_iter": 300, "random_state": 42}

    # Step 1: try every k and record the error (SSE) for each
    sse = []
    for k in range(1, 50):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(df)
        sse.append(kmeans.inertia_)

    # Step 2: use the elbow method to pick the best k
    kl = KneeLocator(range(1, 50), sse, curve="convex", direction="decreasing")
    best_k = kl.elbow
    if best_k is None:
        raise ValueError("Elbow method could not find a best k")
    print(f"Elbow method picked k = {best_k}")

    # Step 3: train the final model with the best k (not the last one from the loop)
    final_model = KMeans(n_clusters=best_k, **kmeans_kwargs)
    final_model.fit(df)

    # Save the final model
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        pickle.dump(final_model, f)

    return sse  # list is JSON-safe


def load_model_elbow(filename: str, sse: list):
    """
    Loads the saved model and scaler, scales the test data the same way
    as the training data, and returns the predicted cluster (as a plain int).
    """
    # load the saved final model (trained with the elbow's best k)
    output_path = os.path.join(os.path.dirname(__file__), "../model", filename)
    loaded_model = pickle.load(open(output_path, "rb"))
    print(f"Loaded model has {loaded_model.n_clusters} clusters")

    # elbow for information/logging
    kl = KneeLocator(range(1, 50), sse, curve="convex", direction="decreasing")
    print(f"Optimal no. of clusters: {kl.elbow}")

    # load the scaler that was fitted on the training data
    scaler_path = os.path.join(os.path.dirname(__file__), "../model", "scaler.pkl")
    scaler = pickle.load(open(scaler_path, "rb"))

    # scale the test data the same way as the training data, then predict
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/test.csv"))
    test_scaled = scaler.transform(df[REQUIRED_COLUMNS])
    print(f"Test customer after scaling: {test_scaled[0]}")
    pred = loaded_model.predict(test_scaled)[0]

    # ensure JSON-safe return
    try:
        return int(pred)
    except Exception:
        # if not numeric, still return a JSON-friendly version
        return pred.item() if hasattr(pred, "item") else pred