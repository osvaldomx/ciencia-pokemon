# src/api/main.py
import os
import joblib
import mlflow
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.api.utils import get_dominant_color

# --- Configuración de la App ---
app = FastAPI(
    title="Pokemon Type Predictor API",
    description="Una API para predecir el tipo de un Pokémon basado en su color RGB.",
    version="0.1.0",
)

# --- Variables Globales para los Modelos ---
# Inicializamos los modelos como None. Se cargarán durante el evento 'startup'.
model = None
mlb = None

# --- Eventos del Ciclo de Vida de la Aplicación ---
@app.on_event("startup")
def load_models():
    """
    Esta función se ejecuta una sola vez cuando la aplicación FastAPI se inicia.
    Carga los modelos desde MLflow y los asigna a las variables globales.
    """
    global model, mlb
    
    print("Cargando modelos desde MLflow...")

    # Usamos la variable de entorno para la URI de MLflow, con un default para local
    default_mlflow_uri = "http://127.0.0.1:5001"
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", default_mlflow_uri)
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    # El RUN_ID también puede venir de una variable de entorno para mayor flexibilidad
    run_id = os.getenv("MLFLOW_RUN_ID", "f59ab49f691d427ea860087faaf7b041") 
    
    # Cargar el modelo de clasificación
    logged_model_uri = f"runs:/{run_id}/pokemon_classifier"
    model = mlflow.pyfunc.load_model(logged_model_uri)
    
    # Cargar el binarizador
    client = mlflow.tracking.MlflowClient()
    local_path = client.download_artifacts(run_id=run_id, path="mlb.joblib")
    mlb = joblib.load(local_path)
    
    print("Modelos cargados exitosamente.")

# --- Modelos de Datos (Pydantic) ---
class PokemonColor(BaseModel):
    dominant_r: int
    dominant_g: int
    dominant_b: int

class PredictionOut(BaseModel):
    predicted_types: list[str]

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de predicción de tipos de Pokémon"}

@app.post("/predict_by_color", response_model=PredictionOut)
def predict_by_color(pokemon_color: PokemonColor) -> PredictionOut:
    """
    Predice los tipos de un Pokémon a partir de su color dominante RGB.
    """
    # El endpoint ahora usa los modelos cargados en las variables globales.
    input_df = pd.DataFrame([pokemon_color.model_dump()])
    prediction_bin = model.predict(input_df)
    predicted_types = mlb.inverse_transform(prediction_bin)
    flat_types = [t for types_tuple in predicted_types for t in types_tuple if t != 'None']
    
    return PredictionOut(predicted_types=flat_types)

@app.get("/predict_by_pokemon/{identifier}", response_model=PredictionOut)
def predict_by_pokemon_identifier(identifier: str) -> PredictionOut:
    """
    Predice los tipos de un Pokémon a partir de su nombre o ID.
    """
    # 1. Consultar la PokéAPI
    try:
        pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{identifier.lower()}"
        response = requests.get(pokeapi_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail=f"Pokémon '{identifier}' no encontrado.")

    sprite_url = data["sprites"]["front_default"]
    if not sprite_url:
        raise HTTPException(status_code=404, detail=f"No se encontró imagen para '{identifier}'.")

    # 2. Calcular el color dominante en tiempo real
    rgb_color = get_dominant_color(sprite_url)
    if rgb_color is None:
        raise HTTPException(status_code=500, detail="No se pudo procesar la imagen del Pokémon.")

    r, g, b = rgb_color

    # 3. Predecir con el modelo cargado
    input_df = pd.DataFrame([{
        "dominant_r": r,
        "dominant_g": g,
        "dominant_b": b
    }])
    prediction_bin = model.predict(input_df)
    predicted_types = mlb.inverse_transform(prediction_bin)
    flat_types = [t for types_tuple in predicted_types for t in types_tuple if t != 'None']

    return PredictionOut(predicted_types=flat_types)