import time
import json
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId, Binary, Timestamp


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
collection = db["Avellino_Redditi"]  # Collection che contiene i dati dei redditi

# Pipeline di aggregazione per calcolare la media del reddito
pipeline = [
    {
        "$group": {
            "_id": None,  # Non raggruppiamo, vogliamo la media globale
            "media_reddito": {"$avg": "$Reddito Imponibile"}
        }
    }
]

# Avvia il timer
start_time = time.time()

# Esegue la query di aggregazione
result = collection.aggregate(pipeline)

# Calcola il tempo di esecuzione
end_time = time.time()
execution_time = end_time - start_time  # Tempo in secondi

# Stampa il risultato
for record in result:
    print(f"Media del reddito imponibile per Avellino: {record['media_reddito']}")

# Stampa il tempo di esecuzione
print(f"Tempo totale di esecuzione: {execution_time:.4f} secondi")

# Salva l'explain in un file JSON utilizzando custom_serializer
explain_result = db.command("aggregate", "Avellino_Redditi", pipeline=pipeline, explain=True)
with open('explain_result_query_reddito_medio.json', 'w') as f:
    json.dump(explain_result, f, indent=4, default=custom_serializer)

print("L'explain è stato salvato.")