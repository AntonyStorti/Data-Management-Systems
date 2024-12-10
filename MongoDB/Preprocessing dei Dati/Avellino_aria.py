import pandas as pd
import json
import copy

# Percorsi dei file
csv_path = 'Avellino/filtered_avellino.csv'
json_input_path = 'Avellino/Stazioni Campania.geojson'
json_output_path = 'Avellino/Avellino_qualità_aria.geojson'

# Carica il CSV
df_avellino = pd.read_csv(csv_path)

# Rimuove spazi bianchi dai nomi delle colonne
df_avellino.columns = df_avellino.columns.str.strip()

# Carica il JSON di input
with open(json_input_path, 'r') as json_file:
    json_data = json.load(json_file)

# Lista dei campi da rimuovere dal JSON
fields_to_remove = [
    "PM10", "PM2_5", "NOX_NO2", "CO", "BENZENE", "O3", "SO2", "LAT", "LONG"
]

# Rimuove i campi indesiderati dalle feature del JSON
for feature in json_data['features']:
    for field in fields_to_remove:
        if field in feature['properties']:
            del feature['properties'][field]

# Lista delle feature aggiornate con tracciamento delle combinazioni uniche
updated_features = []
missing_matches = 0  # Conta le righe senza corrispondenza
unique_entries = set()  # Usato per tracciare le combinazioni 'Name', 'inquinante', 'data_ora'

for index, row in df_avellino.iterrows():
    descrizione_normalized = row['descrizione'].strip().lower()
    inquinante = row['inquinante']
    data_ora = row['data_ora']

    matching_feature = None
    for feature in json_data['features']:
        geojson_name = feature['properties']['Name'].strip().lower()

        if geojson_name == descrizione_normalized:
            matching_feature = feature
            break

    if matching_feature:
        # Creare una chiave unica per identificare duplicati
        unique_key = (matching_feature['properties']['Name'], inquinante, data_ora)

        if unique_key not in unique_entries:
            # Clona la feature per evitare sovrascritture
            cloned_feature = copy.deepcopy(matching_feature)

            # Aggiorna la feature clonata con i dati del CSV
            cloned_feature['properties']['inquinante'] = inquinante
            cloned_feature['properties']['um'] = row['um']
            cloned_feature['properties']['data_ora'] = data_ora
            cloned_feature['properties']['valore'] = row['valore']

            # Aggiungi la feature aggiornata e registra la combinazione unica
            updated_features.append(cloned_feature)
            unique_entries.add(unique_key)  # Segna questa combinazione come elaborata
        else:
            print(f"Duplicato ignorato per {unique_key}")
    else:
        missing_matches += 1

# Aggiorna solo le feature che hanno trovato una corrispondenza
json_data['features'] = updated_features

# Salva il nuovo JSON con tutte le feature
with open(json_output_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Stampa il numero di feature nel GeoJSON di output
print(f"Il file JSON di output contiene {len(json_data['features'])} features.")
print(f"Righe del CSV senza corrispondenza: {missing_matches}")
