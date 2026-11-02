from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from predict import predict_data, get_model_info

app = FastAPI(
    title="Iris Species Prediction API",
    description="Predicts the iris flower species from 4 measurements using a Random Forest model.",
)


class IrisData(BaseModel):
    """
    Flower measurements in centimeters.
    Each value must be greater than 0 and less than 10, since real iris flowers fall in that range.
    """
    sepal_length: float = Field(gt=0, lt=10, description="Sepal length in cm")
    sepal_width: float = Field(gt=0, lt=10, description="Sepal width in cm")
    petal_length: float = Field(gt=0, lt=10, description="Petal length in cm")
    petal_width: float = Field(gt=0, lt=10, description="Petal width in cm")


class IrisResponse(BaseModel):
    class_id: int
    species: str
    confidence: float


class ModelInfo(BaseModel):
    model_type: str
    test_accuracy: float
    species: list[str]


@app.get("/", status_code=status.HTTP_200_OK)
async def health_ping():
    """Check that the API is running."""
    return {"status": "healthy"}


@app.get("/model-info", response_model=ModelInfo)
async def model_info():
    """Return the model type, its test accuracy, and the species it can predict."""
    return get_model_info()


@app.post("/predict", response_model=IrisResponse)
async def predict_iris(iris_features: IrisData):
    """
    Predict the iris species from flower measurements.
    Returns the class number, species name, and the model's confidence.
    """
    try:
        features = [[iris_features.sepal_length, iris_features.sepal_width,
                     iris_features.petal_length, iris_features.petal_width]]
        result = predict_data(features)
        return IrisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))