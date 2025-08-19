
# Ciencia Pokémon: Un Proyecto End-to-End de MLOps

<center>

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![DVC](https://img.shields.io/badge/DVC-8E44AD?style=for-the-badge&logo=dvc&logoColor=white)](https://dvc.org/)

</center>

Este proyecto demuestra un ciclo de vida completo de MLOps, desde la recolección de datos y el entrenamiento del modelo hasta el despliegue de una API en un contenedor Docker. El objetivo es predecir el/los tipo(s) de un Pokémon (ej. Fuego, Agua) basándose en el color dominante de su sprite.

El enfoque principal no es la precisión del modelo, sino la implementación de una arquitectura robusta, reproducible y automatizada utilizando herramientas estándar de la industria.


## Arquitectura MLOps

El proyecto sigue un flujo de trabajo estructurado que asegura la reproducibilidad y la calidad en cada etapa:

* 📦 **Versionamiento de Datos y Modelos**: Se utiliza **DVC (Data Version Control)** para rastrear datasets y modelos, desacoplando los archivos grandes de Git.

* **🧪 Seguimiento de Experimentos**: **MLflow** se utiliza para registrar cada experimento, incluyendo parámetros, métricas y los artefactos generados, permitiendo una trazabilidad completa.

* 🚀 **Despliegue como Servicio**: El modelo entrenado se expone a través de una API RESTful construida con **FastAPI**, que es rápida y ofrece documentación interactiva automática.

* 🐳 **Contenerización**: La aplicación de la API está completamente encapsulada en una imagen de **Docker**, garantizando que el entorno de ejecución sea consistente y portable.

* 🤖 **Integración Continua (CI)**: Se configura un pipeline con GitHub Actions que ejecuta automáticamente las pruebas unitarias (`pytest`) en cada `push`, asegurando la integridad del código.

## Stack Tecnológico

* **Lenguaje**: Python 3.11
* **Framework de API**: FastAPI
* **Contenerización**: Docker
* **MLOps Tools**: MLflow, DVC
* **Librerías de ML**: Scikit-learn, Pandas, NumPy
* **Pruebas**: Pytest, Unittest.mock

## Cómo Ejecutar el Proyecto 🚀

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

**Prerrequisitos**

* Git
* Python 3.11+ y `pip`
* Docker y Docker Compose
* DVC (`pip install dvc[gdrive]`)

**Ejecución Local**

Este método es ideal para el desarrollo y la experimentación.

1. **Clonar el Repositorio:**

```Bash
git clone https://github.com/osvaldomx/ciencia-pokemon.git
cd ciencia-pokemon
```

2. **Crear Entorno Virtual e Instalar Dependencias:**
```Bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Descargar los Datos Versionados:**

```Bash
dvc pull
```

Esto descargará el archivo `pokemon_data.csv` desde el almacenamiento remoto de DVC.

4. **Iniciar el Servidor MLflow:**

En una terminal separada, inicia el servidor de seguimiento para que la API pueda cargar el modelo.

```Bash
mlflow server --host 127.0.0.1 --port 5000
```

5. **Ejecutar la API con Uvicorn:**
En otra terminal, inicia la API.

```Bash
uvicorn src.api.main:app --reload
```

6. **Probar:** Abre tu navegador y ve a `http://127.0.0.1:8000/docs` para acceder a la documentación interactiva y probar el endpoint `/predict`.

## Ejecución con Docker (Recomendado)

Este método simula un entorno de producción y es la forma recomendada de ejecutar la aplicación.

1. **Clonar y Descargar Datos:**
Asegúrate de haber clonado el repositorio y ejecutado `dvc pull` como se describe en los pasos 1 y 3 de la ejecución local.

2. **Iniciar el Servidor MLflow:**
Es crucial iniciar el servidor MLflow para que acepte conexiones desde el contenedor Docker.

```Bash
mlflow server --host 0.0.0.0 --port 5000
```

3. **Construir la Imagen Docker:**

```Bash
docker build -t pokemon-api .
```

4. **Ejecutar el Contenedor:**
Reemplaza `TU_RUN_ID_AQUI` con el ID de tu ejecución de MLflow (puedes encontrarlo en la UI de MLflow o en la salida del script de entrenamiento).

```Bash
docker run -p 8000:8000 \
  -e MLFLOW_TRACKING_URI="http://host.docker.internal:5000" \
  -e MLFLOW_RUN_ID="TU_RUN_ID_AQUI" \
  -e no_proxy="127.0.0.1,localhost,host.docker.internal" \
  pokemon-api
```

5. **Probar:** Abre tu navegador y ve a `http://127.0.0.1:8000/docs`.

## Pruebas Automatizadas 🧪

El proyecto incluye un conjunto de pruebas unitarias para validar la funcionalidad de la API sin depender de servicios externos.

Para ejecutar las pruebas:

```Bash
python -m pytest
```

Las pruebas utilizan `unittest.mock` para simular las llamadas al servidor MLflow, lo que las hace rápidas, confiables e ideales para ejecutarse en un entorno de CI.

## Licencia
Este proyecto está bajo la Licencia GPL-3.0. Ver el archivo LICENSE para más detalles.