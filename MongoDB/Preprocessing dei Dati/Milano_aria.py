import pandas as pd
import geojson
from datetime import datetime

# Caricamento dei CSV
csv1_path = 'Milano/Milano_stazioni_qualità__dell_aria.csv'
csv2_path = 'Milano/Milano_aria.csv'

# Carica i dati dei CSV
df1 = pd.read_csv(csv1_path)
df2 = pd.read_csv(csv2_path)

print(f"Numero di righe in df1: {len(df1)}")
print(f"Numero di righe in df2: {len(df2)}")

# Rinomina la colonna ID nel secondo dataframe per permettere il merge
df2 = df2.rename(columns={"idsensore": "IdSensore"})

# Estrazione delle coordinate dalla colonna Location (formato POINT (lng lat))
coords = df1['Location'].str.extract(r'POINT \(([^ ]+) ([^ ]+)\)')
df1['Longitude'] = coords[0].astype(float)
df1['Latitude'] = coords[1].astype(float)

# Merge dei DataFrame basato sull'IdSensore
merged_df = pd.merge(df1, df2, on="IdSensore")
print(f"Numero di righe dopo il merge: {len(merged_df)}")


# Funzione per pulire le righe rimuovendo i NaN dalle proprietà
def clean_row(row):
    cleaned = {k: v for k, v in row.items() if pd.notna(v)}
    return cleaned


# Funzione per convertire la data nel formato Date di MongoDB
def convert_to_mongo_date(date_str):
    if pd.isna(date_str):  # Controllo se la data è NaN
        return None
    try:
        # Sostituire la virgola con il punto per il formato dei millisecondi
        if isinstance(date_str, str):
            date_str = date_str.replace(',', '.')
        # Converte la data nel formato MongoDB Date (ISO 8601)
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f").isoformat()
    except ValueError:
        print(f"Errore nella conversione della data: formato non valido per '{date_str}'")
        return None


# Funzione per convertire le date in formato 'dd/mm/yyyy' nel formato ISO 8601
def convert_date_format(date_str):
    if pd.isna(date_str):  # Controllo se la data è NaN
        return None
    try:
        # Converte la data nel formato ISO 8601
        return datetime.strptime(date_str, "%d/%m/%Y").isoformat()
    except ValueError:
        print(f"Errore nella conversione della data: formato non valido per '{date_str}'")
        return None


# Creazione delle Feature GeoJSON
features = []
for _, row in merged_df.iterrows():
    # Creazione di un punto GeoJSON
    point = geojson.Point((row['Longitude'], row['Latitude']))

    # Pulisce la riga rimuovendo le colonne vuote
    row_cleaned = clean_row(row.drop(['Latitude', 'Longitude', 'Location']))

    # Rinominare i campi nelle proprietà
    row_cleaned['Name'] = row_cleaned.pop('NomeStazione', None)
    row_cleaned['inquinante'] = row_cleaned.pop('NomeTipoSensore', None)
    row_cleaned['um'] = row_cleaned.pop('UnitaMisura', None)

    # Converte la data nel formato MongoDB Date, se possibile
    data_ora = convert_to_mongo_date(row_cleaned.pop('data', None))
    if data_ora:
        row_cleaned['data_ora'] = data_ora

    # Converte 'DataStart' e 'DataStop' nel formato ISO 8601
    data_start = convert_date_format(row_cleaned.pop('DataStart', None))
    if data_start:
        row_cleaned['DataStart'] = data_start

    data_stop = convert_date_format(row_cleaned.pop('DataStop', None))
    if data_stop:
        row_cleaned['DataStop'] = data_stop

    # Rinominare 'Comune' in 'COMUNE'
    row_cleaned['COMUNE'] = row_cleaned.pop('Comune', None)

    # Rimuovere i campi non necessari
    row_cleaned.pop('Storico', None)
    row_cleaned.pop('Utm_Nord', None)
    row_cleaned.pop('UTM_Est', None)
    row_cleaned.pop('lat', None)
    row_cleaned.pop('lng', None)
    row_cleaned.pop('IdSensore', None)

    # Crea una Feature con attributi
    feature = geojson.Feature(geometry=point, properties=row_cleaned)
    features.append(feature)

# Crea il FeatureCollection GeoJSON
feature_collection = geojson.FeatureCollection(features)

# Stampa finale per il numero di feature
print(f"Numero di feature nel GeoJSON: {len(features)}")

# Salva il file GeoJSON
with open('Milano/Milano_qualità_aria.geojson', 'w') as f:
    geojson.dump(feature_collection, f)

print("File GeoJSON creato con successo: Milano_qualità_aria.geojson")
