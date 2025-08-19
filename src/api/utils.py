# src/api/utils.py
import requests
from PIL import Image
import numpy as np
from io import BytesIO

def get_dominant_color(image_url: str) -> tuple[int, int, int] | None:
    """
    Descarga una imagen desde una URL y calcula su color RGB dominante.
    Ignora los píxeles transparentes. Devuelve None si falla.
    """
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img_array = np.array(img)

        opaque_pixels = img_array[img_array[:, :, 3] > 0][:, :3]

        if len(opaque_pixels) == 0:
            return 0, 0, 0

        dominant_color = opaque_pixels.mean(axis=0)
        return int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2])

    except requests.exceptions.RequestException:
        return None