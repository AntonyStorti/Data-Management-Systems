import csv
import json
import time
from pymongo import MongoClient
from bson import ObjectId, Binary, Timestamp
from datetime import datetime

# Funzione per serializzare oggetti non JSON serializzabili
def custom_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Converte ObjectId in stringa
    elif isinstance(obj, Binary):
        return obj.hex()  # Converte Binary in stringa esadecimale
    elif isinstance(obj, bytes):
        return obj.hex()  # Converte bytes in stringa esadecimale
    elif isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime in formato ISO string
    elif isinstance(obj, Timestamp):
        return obj.as_datetime().isoformat()  # Converte Timestamp in formato ISO string
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")

# Connessione al database MongoDB
client = MongoClient("mongodb://localhost:27141/")
db = client["Impianti_Fotovoltaici"]

consumi_collection = db["Consumi_Elettrici"]
omi_collection = db["Avellino_OMI"]

# Aggregazione per calcolare la media dei consumi per ogni zona OMI
pipeline = [
    {
        "$match": {
            "città": "Avellino"  # Filtra i documenti per città Avellino
        }
    },
    {
        "$lookup": {
            "from": "Avellino_OMI",  # Collezione da cui fare il join
            "localField": "OMI",      # Campo nella collezione Consumi_Elettrici
            "foreignField": "_id",    # Campo nella collezione Avellino_OMI
            "as": "zona_info"         # Alias per i dati uniti
        }
    },
    {
        "$unwind": "$zona_info"  # Decompone l'array di zone unificate in un singolo documento
    },
    {
        "$group": {
            "_id": "$zona_info.properties.name",  # Raggruppa per nome della zona OMI
            "media_consumo": {
                "$avg": "$consumo_energetico"  # Calcola la media del consumo per zona
            }
        }
    },
    {
        "$project": {
            "_id": 0,  # Esclude l'ID
            "name": "$_id",  # Rinomina _id in name per la zona
            "media_consumo": 1  # Mostra solo la media del consumo
        }
    }
]

# Avvia il timer
start_time = time.time()

# Esegue l'aggregazione e raccogle i risultati in una lista
result = list(consumi_collection.aggregate(pipeline))

# Elenco dei risultati
for document in result:
    print(f"Zona: {document['name']}, Media Consumo: {document['media_consumo']} MWh")

# Calcola il tempo di esecuzione
end_time = time.time()
execution_time = end_time - start_time  # Tempo in secondi

# Stampa il tempo di esecuzione
print(f"Tempo totale di esecuzione: {execution_time:.4f} secondi")

# Salvataggio dei risultati in un file CSV
with open('risultato_query_Avellino_Consumi.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'media_consumo']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()  # Scrive l'intestazione nel CSV

    # Scrive i dati nel CSV
    for document in result:
        writer.writerow({'name': document['name'], 'media_consumo': document['media_consumo']})

print("I risultati sono stati salvati.")

# Salva l'explain in un file JSON utilizzando custom_serializer
explain_result = db.command("aggregate", "Consumi_Elettrici", pipeline=pipeline, explain=True)
with open('explain_result_query_Avellino_Consumi.json', 'w') as f:
    json.dump(explain_result, f, indent=4, default=custom_serializer)

print("L'explain è stato salvato.")
