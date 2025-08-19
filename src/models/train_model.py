# src/models/train_model.py
import pandas as pd
import yaml
import joblib
import os
import mlflow
import dvc.api

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# --- Configuración del Experimento con MLflow ---
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Pokemon Type Prediction")

def train_model():
    """
    Función principal para entrenar el modelo.
    """
    # Cargar parámetros desde params.yaml
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    # Usar la API de DVC para obtener la URL del archivo de datos versionado
    data_url = dvc.api.get_url(
        path=params['data']['raw_path'],
        repo='.', # Repositorio local
        rev='' # Rama o commit
    )

    # Cargar los datos
    df = pd.read_csv(data_url)

    # --- Preprocesamiento de Datos ---
    # Rellenar valores nulos en 'type2'
    df['type2'].fillna('None', inplace=True)

    # Crear las etiquetas (y) combinando los tipos en una lista
    y_raw = df[['type1', 'type2']].values.tolist()

    # Usar MultiLabelBinarizer para convertir las etiquetas a formato binario
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(y_raw)

    # Definir las características (X)
    features = ['dominant_r', 'dominant_g', 'dominant_b']
    X = df[features]

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=params['training']['test_size'], 
        random_state=params['training']['random_state']
    )

    print("Datos cargados y procesados con éxito.")
    print(f"Tamaño del set de entrenamiento: {X_train.shape[0]} muestras")
    print(f"Tamaño del set de prueba: {X_test.shape[0]} muestras")

    # --- Entrenamiento y Seguimiento con MLflow ---
    with mlflow.start_run():
        print("Iniciando ejecución de MLflow...")

        # Inicializar y entrenar el modelo
        model_params = params['model']['params']
        model = KNeighborsClassifier(**model_params)
        model.fit(X_train, y_train)

        # Realizar predicciones
        y_pred = model.predict(X_test)

        # Calcular métricas
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='micro') # 'micro' es bueno para multi-etiqueta
        precision = precision_score(y_test, y_pred, average='micro')
        recall = recall_score(y_test, y_pred, average='micro')

        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Score (micro): {f1:.4f}")

        # Registrar parámetros y métricas en MLflow
        mlflow.log_params(model_params)
        mlflow.log_param("random_state", params['training']['random_state'])
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score_micro", f1)
        mlflow.log_metric("precision_micro", precision)
        mlflow.log_metric("recall_micro", recall)

        # Guardar y registrar el binarizador como un artefacto
        binarizer_path = "models/mlb.joblib"
        os.makedirs("models", exist_ok=True)
        joblib.dump(mlb, binarizer_path)
        mlflow.log_artifact(binarizer_path)

        # Registrar el modelo en MLflow
        mlflow.sklearn.log_model(model, "pokemon_classifier")

        print("Modelo, binarizador y métricas guardadas en MLflow.")

if __name__ == "__main__":
    train_model()