import pandas as pd
import pymongo
import os
import time
from pymongo import InsertOne
from pymongo.errors import BulkWriteError
from bson.decimal128 import Decimal128
from datetime import datetime

# Connessione al router MongoS
client = pymongo.MongoClient("mongodb://localhost:27141")

# Effettua la connessione al database admin per abilitare lo sharding
admin_db = client.admin

# Abilita lo sharding sul database Impianti_Fotovoltaici
try:
    admin_db.command("enableSharding", "Impianti_Fotovoltaici")
    print("Sharding abilitato per il database.")
except Exception as e:
    print(f"Errore nell'abilitare lo sharding: {e}")
    exit(1)

# Shardare la collezione Milano su una chiave composta
try:
    admin_db.command("shardCollection", "Impianti_Fotovoltaici.Milano",
                     key={"Soggetto": 1, "Data di Nascita": 1, "Reddito Imponibile": 1})
    print("Collezione shardata.")
except Exception as e:
    print(f"Errore nello shardare la collezione: {e}")
    exit(1)

# Seleziona il database e la collezione
db = client["Impianti_Fotovoltaici"]
collection = db["Milano"]

# Percorso del file CSV
csv_file_path = "./Milano/Milano.csv"

# Verifica che il file CSV esista
if not os.path.isfile(csv_file_path):
    print(f"Il file {csv_file_path} non esiste.")
    exit(1)

# Carica il file CSV in un DataFrame Pandas
try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Errore nella lettura del file CSV: {e}")
    exit(1)


# Funzione per convertire i tipi di dato ed escludere i campi NaN
def convert_types(row):
    document = {}
    try:
        # Se il campo non è NaN, viene aggiunto al documento
        if pd.notna(row["Soggetto"]):
            document["Soggetto"] = str(row["Soggetto"])  # Assicurarsi che sia stringa

        if pd.notna(row["Data di Nascita"]):
            # Converti in datetime.datetime
            document["Data di Nascita"] = datetime.strptime(row["Data di Nascita"], "%Y-%m-%d")  # Converte in datetime

        if pd.notna(row["Categoria di Reddito"]):
            document["Categoria di Reddito"] = str(row["Categoria di Reddito"])  # Assicurarsi che sia stringa

        if pd.notna(row["Reddito Imponibile"]):
            document["Reddito Imponibile"] = Decimal128(str(row["Reddito Imponibile"]))  # Converte in Decimal128

        if pd.notna(row["Imposta Netta"]):
            document["Imposta Netta"] = Decimal128(str(row["Imposta Netta"]))  # Converte in Decimal128

        if pd.notna(row["Reddito d'Impresa / Lavoro Autonomo"]):
            document["Reddito d'Impresa / Lavoro Autonomo"] = Decimal128(
                str(row["Reddito d'Impresa / Lavoro Autonomo"]))  # Converte in Decimal128

        if pd.notna(row["Volume d'Affari"]):
            document["Volume d'Affari"] = Decimal128(str(row["Volume d'Affari"]))  # Converte in Decimal128

        if pd.notna(row["Tipo Modello"]):
            document["Tipo Modello"] = str(row["Tipo Modello"])  # Assicurarsi che sia stringa

    except Exception as e:
        print(f"Errore nella conversione dei tipi: {e}")

    return document


# Applicare la conversione dei tipi a ogni riga del DataFrame
data = df.apply(convert_types, axis=1).tolist()  # Converte in lista di documenti

# Filtra i documenti per rimuovere eventuali dizionari vuoti
data = [doc for doc in data if doc]  # Rimuove documenti vuoti

# Converti i dati in operazioni InsertOne
operations = [InsertOne(doc) for doc in data]

# Inserimento in batch
batch_size = 50000
for i in range(0, len(operations), batch_size):
    try:
        # Esegue il bulk_write con il batch corrente
        result = collection.bulk_write(operations[i:i + batch_size])
        print(f"Batch {i // batch_size + 1} inserito con successo: {result.inserted_count} documenti inseriti.")
        time.sleep(60)  # Ritardo tra i batch per evitare sovraccarichi
    except BulkWriteError as e:
        print(f"Errore nell'inserimento del batch a partire dall'indice {i}: {e.details}")

print("Caricamento completato.")
