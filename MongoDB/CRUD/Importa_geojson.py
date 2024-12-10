import json
from pymongo import MongoClient
from datetime import datetime

# Connessione a MongoDB
client = MongoClient("mongodb://localhost:27141")
db = client["Impianti_Fotovoltaici"]
collection = db["Inquinanti_Aria"]

# Legge il file GeoJSON
with open("../Napoli/Napoli_qualità_aria.geojson") as f:
    geojson_data = json.load(f)

# Estrae le features, modifica i dati e li inserisce come documenti separati
features = geojson_data["features"]
for feature in features:
    # Rimuove il campo "type" se presente
    feature.pop("type", None)

    # Rimuove la coordinata che vale 0 se presente
    if "geometry" in feature and "coordinates" in feature["geometry"]:
        coordinates = feature["geometry"]["coordinates"]
        if len(coordinates) > 2 and coordinates[2] == 0:
            feature["geometry"]["coordinates"] = coordinates[:2]

    # Converte properties.data_ora in un tipo datetime se esiste
    if "properties" in feature and "data_ora" in feature["properties"]:
        data_ora_str = feature["properties"]["data_ora"]
        try:
            # Aggiunge i due punti nel fuso orario se manca (+01 diventa +01:00)
            if data_ora_str[-3] == '+' or data_ora_str[-3] == '-':
                data_ora_str = data_ora_str[:-3] + data_ora_str[-3:] + ":00"

            # Converte la stringa al formato datetime
            feature["properties"]["data_ora"] = datetime.strptime(
                data_ora_str, "%Y-%m-%d %H:%M:%S%z"
            )
        except ValueError as e:
            print(f"Errore di parsing data: {data_ora_str} - {e}")

    # Converte properties.valore in un tipo numerico (int o float)
    if "properties" in feature and "valore" in feature["properties"]:
        valore_str = feature["properties"]["valore"]
        try:
            # Prova a convertire a float, se fallisce prova con int
            feature["properties"]["valore"] = float(valore_str) if '.' in str(valore_str) else int(valore_str)
        except ValueError as e:
            print(f"Errore di parsing valore: {valore_str} - {e}")
            feature["properties"]["valore"] = None  # Imposta a None se non è un numero valido

# Inserisce i documenti nella collezione MongoDB
collection.insert_many(features)

print("Dati importati correttamente.")
