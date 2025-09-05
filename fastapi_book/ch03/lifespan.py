
from contextlib import asynccontextmanager
from fastapi import FastAPI

def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("Loading the ML models...")
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    print("ML models loaded.")
    yield
    print("Cleaning up the ML models...")
    # Clean up the ML models and release the resources
    ml_models.clear()
    print("ML models cleaned up.")