import requests
import pandas as pd
from tqdm import tqdm
import os

BASE_URL = "https://pokeapi.co/api/v2/pokemon/{id}"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{id}"
TOTAL_POKEMON = 1025
OUTPUT_FILE = "data/raw/pokemon_full_stats.csv"

def fetch_all_pokemon_data():
    pokemon_list = []
    for i in tqdm(range(1, TOTAL_POKEMON + 1), desc="Fetching Pokémon Data"):
        try:
            # Primera llamada para stats básicos
            res_main = requests.get(BASE_URL.format(id=i)).json()
            # Segunda llamada para datos de especie
            res_species = requests.get(SPECIES_URL.format(id=i)).json()

            # Extraer datos...
            info = {
                "id": i,
                "name": res_main['name'],
                "type1": res_main['types'][0]['type']['name'],
                "type2": res_main['types'][1]['type']['name'] if len(res_main['types']) > 1 else None,
                "hp": next(s['base_stat'] for s in res_main['stats'] if s['stat']['name'] == 'hp'),
                "attack": next(s['base_stat'] for s in res_main['stats'] if s['stat']['name'] == 'attack'),
                "defense": next(s['base_stat'] for s in res_main['stats'] if s['stat']['name'] == 'defense'),
                "speed": next(s['base_stat'] for s in res_main['stats'] if s['stat']['name'] == 'speed'),
                "height": res_main['height'],
                "weight": res_main['weight'],
                "abilities": [a['ability']['name'] for a in res_main['abilities']],
                "generation": res_species['generation']['name'],
                "catch_rate": res_species['capture_rate'],
                "category": next(g['genus'] for g in res_species['genera'] if g['language']['name'] == 'en'),
            }
            pokemon_list.append(info)
        except Exception as e:
            print(f"Failed to fetch data for Pokémon ID {i}: {e}")
    return pd.DataFrame(pokemon_list)

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    df = fetch_all_pokemon_data()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Dataset completo guardado en {OUTPUT_FILE}")