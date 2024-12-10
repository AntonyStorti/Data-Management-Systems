import pandas as pd
import json

# Caricare i CSV
csv1 = pd.read_csv("Venezia/Stazioni Venezia.csv")
csv2 = pd.read_csv("Venezia/Venezia_aria.csv")

# Unire i CSV in base ai campi 'Identificatore SIRAV' = 'idsensore' e 'inquinante'
merged_data = pd.merge(csv1, csv2, left_on=['Identificatore SIRAV', 'inquinante'], right_on=['idsensore', 'inquinante'], how='inner')

# Creare il GeoJSON
features = []

for _, row in merged_data.iterrows():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row['Longitudine'], row['Latitudine']]  # Longitudine, Latitudine
        },
        "properties": {
            "COMUNE": row['COMUNE'],
            "Provincia": row['Provincia'],
            "Indirizzo": row['Indirizzo'],
            "Name": row['Name'],
            "Tipo stazione": row['Tipo stazione'],
            "inquinante": row['inquinante'],
            "valore": row['valore'],
            "quota": row['Altitudine'],
            "idsensore": row['Identificatore SIRAV'],
            "data_ora": row['data']
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Salvare il GeoJSON in un file
with open("Venezia/Venezia_qualità_aria.geojson", "w") as f:
    json.dump(geojson, f, indent=4)

print("GeoJSON creato con successo!")

# Stampare il numero di features
print(f"Numero di features nel GeoJSON: {len(features)}")