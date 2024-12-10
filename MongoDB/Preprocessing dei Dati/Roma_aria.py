import pandas as pd
import geojson
from shapely.geometry import Point
from datetime import datetime

# Carica i CSV
csv1 = pd.read_csv('Roma/Stazioni Roma.csv')
csv2 = pd.read_csv('Roma/Roma_aria.csv')

# Unisce i CSV in base ai campi 'codice stazione' (csv1) e 'idsensore' (csv2), e 'inquinante'
merged_df = pd.merge(csv1, csv2, left_on=['codice stazione', 'inquinante'], right_on=['idsensore', 'inquinante'])

# Crea una lista per le feature GeoJSON
features = []

# Crea le feature GeoJSON
for index, row in merged_df.iterrows():
    # Crea un punto usando latitudine e longitudine
    point = Point(row['longitudine'], row['latitudine'])

    # Converte la data in formato 'Date' (ISO 8601 senza millisecondi)
    data_ora = row['data'].split(',')[0]  # Rimuove la parte dopo la virgola
    # Converte la data in oggetto datetime
    data_ora_mongo = datetime.fromisoformat(data_ora)

    # Converte la data in formato stringa ISO 8601 (per evitare problemi di serializzazione)
    data_ora_iso = data_ora_mongo.isoformat()  # Usa isoformat per ottenere una stringa ISO 8601

    # Crea il dizionario della feature GeoJSON
    feature = geojson.Feature(
        geometry=geojson.Point((row['longitudine'], row['latitudine'])),
        properties={
            'codice stazione': row['codice stazione'],
            'Name': row['Località stazione'],
            'COMUNE': row['COMUNE'],
            'inquinante': row['inquinante'],
            'data_ora': data_ora_iso,
            'valore': row['valore']
        }
    )
    features.append(feature)

# Stampa il numero di features
print(f"Total number of features: {len(features)}")

# Crea il dizionario GeoJSON finale
feature_collection = geojson.FeatureCollection(features)

# Scrive il file GeoJSON
with open('Roma/Roma_qualità_aria.geojson', 'w') as f:
    geojson.dump(feature_collection, f)

print("GeoJSON file created successfully.")
