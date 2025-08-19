# tests/test_api.py
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a la API de predicción de tipos de Pokémon"}

def test_predict_endpoint():
    # Test con el color de Bulbasaur (verde)
    response = client.post("/predict", json={"dominant_r": 76, "dominant_g": 164, "dominant_b": 94})
    assert response.status_code == 200
    # La predicción puede variar, solo verificamos que la estructura sea correcta
    assert "predicted_types" in response.json()
    assert isinstance(response.json()["predicted_types"], list)