from flask import Flask, jsonify, request
import pandas as pd
import random
import time
import csv
from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)

# Variables globales para almacenar el cache
cached_pokemones = []
last_update_time = 0

@app.route('/pokemones', methods=['GET'])
@app.route('/pokemones', methods=['GET'])
def obtener_pokemones():
    global cached_pokemones, last_update_time

    try:
        ruta_csv = os.path.join(BASE_DIR, "pokemon.csv")
        df = pd.read_csv(ruta_csv, encoding='latin1')

        # Verifica que la columna 'NOMBRE' exista
        if "NOMBRE" not in df.columns:
            return jsonify({"error": "La columna 'NOMBRE' no se encuentra en el archivo"}), 400

        # Si han pasado más de 3600 segundos o no hay caché, genera nuevos pokémon
        tiempo_actual = time.time()
        if tiempo_actual - last_update_time > 3600 or not cached_pokemones:
            nombres = df["NOMBRE"].dropna().unique().tolist()
            if len(nombres) == 0:
                return jsonify({"error": "No hay más Pokémon disponibles en el CSV"}), 404

            cantidad_a_seleccionar = min(4, len(nombres))
            cached_pokemones = random.sample(nombres, k=cantidad_a_seleccionar)
            last_update_time = tiempo_actual

            # Eliminar los registros de los pokemones seleccionados
            df = df[~df["NOMBRE"].isin(cached_pokemones)]

            # Guardar el CSV actualizado sin los pokémon seleccionados
            df.to_csv(ruta_csv, index=False, encoding='latin1')
            print(f"Pokémon entregados y eliminados: {cached_pokemones}")

        return jsonify({"pokemones": cached_pokemones}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/intentos', methods=['POST'])
def recibir_intentos():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)

        intentos = data.get("intentos")
        nombre = data.get("nombre")     # Leo o Hector
        pokemon = data.get("pokemon")

        if intentos is None or nombre is None or pokemon is None:
            return jsonify({"error": "Faltan campos 'intentos', 'nombre' o 'pokemon' en el JSON"}), 400

        ruta_csv = os.path.join(BASE_DIR, "pokemon_estadisticas.csv")

        # Leer el archivo CSV
        df = pd.read_csv(ruta_csv)

        # Verificar que las columnas necesarias existen
        if nombre not in df.columns or "nombre" not in df.columns:
            return jsonify({"error": f"No se encontró la columna '{nombre}' o 'nombre' en el archivo"}), 400

        # Verificar si el Pokémon está en la columna "nombre"
        if pokemon not in df["nombre"].values:
            return jsonify({"error": f"El Pokémon '{pokemon}' no se encuentra en la columna 'nombre'"}), 404

        # Actualizar el valor
        df.loc[df["nombre"] == pokemon, nombre] = intentos

        # Guardar cambios en el CSV
        df.to_csv(ruta_csv, index=False)

        print(f"Actualizado: {pokemon} -> {nombre} = {intentos}")

        return jsonify({"mensaje": "Intento actualizado correctamente"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/promedios', methods=['GET'])
def obtener_promedios():
    try:
        ruta_csv = os.path.join(BASE_DIR, "pokemon_estadisticas.csv")
        df = pd.read_csv(ruta_csv)

        promedios = {}

        for jugador in ["Leo", "Hector"]:
            if jugador in df.columns:
                # Filtrar solo los valores distintos de 0
                valores_validos = df[jugador][df[jugador] != 0]

                if not valores_validos.empty:
                    promedio = valores_validos.mean()
                else:
                    promedio = 0  # Si no hay valores válidos

                promedios[jugador] = round(promedio, 2)
            else:
                promedios[jugador] = "Columna no encontrada"

        return jsonify(promedios), 200

    except Exception as e:
        print("Error al calcular promedios:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/ver_csv', methods=['GET'])
def ver_csv():
    try:
        ruta_csv = os.path.join(BASE_DIR, "pokemon.csv")
        df = pd.read_csv(ruta_csv, encoding='latin1')
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





