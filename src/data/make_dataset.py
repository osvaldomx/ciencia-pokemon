# src/data/make_dataset.py
import requests
import pandas as pd
from PIL import Image
import numpy as np
from io import BytesIO
from tqdm import tqdm
import os

# --- Constantes ---
# URL base de la PokeAPI
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{id}"
# Número de Pokémon a procesar (la primera generación)
TOTAL_POKEMON = 251
# Ruta donde se guardarán los datos crudos
OUTPUT_PATH = "data/raw/"
OUTPUT_FILE = os.path.join(OUTPUT_PATH, "pokemon_data.csv")

def get_dominant_color(image_url):
    """
    Descarga una imagen desde una URL y calcula su color RGB dominante.
    Ignora los píxeles transparentes.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Lanza un error si la petición falla
        
        # Abre la imagen desde el contenido de la respuesta
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img_array = np.array(img)

        # Filtra los píxeles que no son completamente transparentes
        # La forma del array es (alto, ancho, 4), donde el 4to canal es el alfa
        opaque_pixels = img_array[img_array[:, :, 3] > 0][:, :3]

        if len(opaque_pixels) == 0:
            return 0, 0, 0 # Devuelve negro si no hay píxeles opacos

        # Calcula el color promedio (dominante)
        dominant_color = opaque_pixels.mean(axis=0)
        return int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2])
    
    except requests.exceptions.RequestException as e:
        print(f"Error descargando la imagen: {e}")
        return None, None, None

def fetch_pokemon_data():
    """
    Obtiene los datos de cada Pokémon desde la PokeAPI y los procesa.
    """
    pokemon_list = []
    print(f"Iniciando la recolección de datos de {TOTAL_POKEMON} Pokémon...")

    # Usamos tqdm para tener una barra de progreso
    for i in tqdm(range(1, TOTAL_POKEMON + 1), desc="Procesando Pokémon"):
        try:
            response = requests.get(POKEAPI_URL.format(id=i))
            response.raise_for_status()
            data = response.json()

            name = data["name"]
            types = [t["type"]["name"] for t in data["types"]]
            sprite_url = data["sprites"]["front_default"]

            if not sprite_url:
                continue # Si no hay sprite, saltamos a la siguiente iteración

            r, g, b = get_dominant_color(sprite_url)
            
            if r is not None:
                pokemon_info = {
                    "id": i,
                    "name": name,
                    "type1": types[0] if len(types) > 0 else None,
                    "type2": types[1] if len(types) > 1 else None,
                    "dominant_r": r,
                    "dominant_g": g,
                    "dominant_b": b,
                }
                pokemon_list.append(pokemon_info)
        
        except requests.exceptions.RequestException as e:
            print(f"No se pudo obtener el Pokémon con ID {i}: {e}")

    return pd.DataFrame(pokemon_list)


if __name__ == "__main__":
    # Asegúrate de que el directorio de salida exista
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # Obtiene los datos y los guarda en un archivo CSV
    df = fetch_pokemon_data()
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n¡Proceso completado! Datos guardados en '{OUTPUT_FILE}'.")
    print("Primeras 5 filas del dataset:")
    print(df.head())