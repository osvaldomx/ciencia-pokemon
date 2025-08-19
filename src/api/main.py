# src/api/main.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import mlflow
import joblib

default_mlflow_uri = "http://127.0.0.1:5000"

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", default_mlflow_uri)
mlflow.set_tracking_uri(mlflow_tracking_uri)

# --- Configuración de la App ---
app = FastAPI(
    title="Pokemon Type Predictor API",
    description="Una API para predecir el tipo de un Pokémon basado en su color RGB.",
    version="0.1.0",
)

# --- Carga de Modelos y Artefactos ---
# Reemplaza con el Run ID de tu mejor experimento en MLflow
RUN_ID = "f59ab49f691d427ea860087faaf7b041" 

# Cargar el modelo de clasificación desde MLflow
logged_model_uri = f"runs:/{RUN_ID}/pokemon_classifier"
model = mlflow.pyfunc.load_model(logged_model_uri)

# Cargar el binarizador de etiquetas desde los artefactos de MLflow
client = mlflow.tracking.MlflowClient()
local_path = client.download_artifacts(run_id=RUN_ID, path="mlb.joblib")
mlb = joblib.load(local_path)

# --- Definición de Modelos de Datos (Pydantic) ---
class PokemonColor(BaseModel):
    dominant_r: int
    dominant_g: int
    dominant_b: int

class PredictionOut(BaseModel):
    predicted_types: list[str]


# --- Endpoints de la API ---
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de predicción de tipos de Pokémon"}

@app.post("/predict", response_model=PredictionOut)
def predict_type(pokemon_color: PokemonColor):
    """
    Predice los tipos de un Pokémon a partir de su color dominante RGB.
    """
    # Crear un DataFrame a partir de los datos de entrada
    input_df = pd.DataFrame([pokemon_color.dict()])

    # Realizar la predicción
    prediction_bin = model.predict(input_df)

    # Invertir la transformación para obtener los nombres de los tipos
    predicted_types = mlb.inverse_transform(prediction_bin)

    # Formatear la salida
    # inverse_transform devuelve una tupla de listas, la aplanamos
    flat_types = [t for types_tuple in predicted_types for t in types_tuple if t != 'None']

    return PredictionOut(predicted_types=flat_types)