import pandas as pd
import json

# Carica i due CSV
csv1 = pd.read_csv("Genova/Stazioni Genova.csv")
csv2 = pd.read_csv("Genova/Genova_aria.csv")

# Effettua il join tra csv1 e csv2 su 'idsensore' e 'inquinante'
merged_df = pd.merge(csv2, csv1, on=['idsensore', 'inquinante'], how='left')

# Crea le feature GeoJSON
features = []
for _, row in merged_df.iterrows():
    if not pd.isna(row['Latitudine']) and not pd.isna(row['Longitudine']):
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['Longitudine'], row['Latitudine']]
            },
            "properties": {
                "COMUNE": row.get("COMUNE"),
                "Provincia": row.get("Provincia"),
                "Name": row.get("Name"),
                "inquinante": row.get("inquinante"),
                "um": row.get("um"),
                "quota": row.get("quota"),
                "Tipologia": row.get("Tipologia"),
                "Località": row.get("Località"),
                "idsensore": row.get("idsensore"),
                "data_ora": row.get("data_ora"),
                "valore": row.get("valore")
            }
        }
        features.append(feature)

# Crea la struttura GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Salva il risultato come file GeoJSON
output_geojson = "Genova_qualità_aria.geojson"
with open(output_geojson, "w") as f:
    json.dump(geojson, f, indent=2)

# Stampa il numero totale di feature
num_features = len(features)
print(f"GeoJSON salvato con successo in: {output_geojson}")
print(f"Numero totale di feature: {num_features}")
