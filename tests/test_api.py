# tests/test_api.py
from fastapi.testclient import TestClient
from src.api.main import app
import numpy as np
from unittest.mock import patch, MagicMock

def test_predict_endpoint_with_mock():
    # Definimos las rutas a parchear
    patch_path_load_model = 'src.api.main.mlflow.pyfunc.load_model'
    patch_path_client = 'src.api.main.mlflow.tracking.MlflowClient' # Parcheamos el cliente completo
    patch_path_joblib = 'src.api.main.joblib.load'

    with patch(patch_path_load_model) as mock_load_model, \
         patch(patch_path_client) as mock_client, \
         patch(patch_path_joblib) as mock_load_joblib:

        # --- Configuración de Mocks ---
        # Configuramos el mock del modelo como antes
        mock_model_instance = MagicMock()
        mock_model_instance.predict.return_value = np.array([[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        mock_load_model.return_value = mock_model_instance

        # Configuramos el mock del binarizador como antes
        mock_mlb_instance = MagicMock()
        mock_mlb_instance.inverse_transform.return_value = [('fire',)]
        mock_load_joblib.return_value = mock_mlb_instance

        # El cliente de MLflow también debe ser mokeado
        mock_client_instance = MagicMock()
        # Su método download_artifacts puede devolver cualquier cosa, no importa
        mock_client_instance.download_artifacts.return_value = "fake/path/model.joblib"
        mock_client.return_value = mock_client_instance

        # --- Ejecución de la Prueba ---
        # ¡IMPORTANTE! Creamos el TestClient DENTRO del bloque with.
        # Esto asegura que los mocks estén activos cuando el cliente
        # ejecute el evento 'startup' y llame a nuestra función load_models().
        with TestClient(app) as client:
            response = client.post("/predict", json={"dominant_r": 239, "dominant_g": 139, "dominant_b": 49})
            
            # --- Verificación ---
            assert response.status_code == 200
            assert response.json() == {"predicted_types": ["fire"]}

def test_read_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Bienvenido a la API de predicción de tipos de Pokémon"}