import csv
import json
import base64
from pymongo import MongoClient
from bson.binary import Binary
from bson import Timestamp

# Funzione per convertire i dati binari, bytes e Timestamp in formati serializzabili
def convert_binary_to_base64(data):
    if isinstance(data, Binary):
        # Converte il dato binario in una stringa base64
        return base64.b64encode(data).decode('utf-8')
    elif isinstance(data, bytes):
        # Se il dato è di tipo bytes, lo converte in base64
        return base64.b64encode(data).decode('utf-8')
    elif isinstance(data, Timestamp):
        # Converte un oggetto Timestamp in una stringa (ISO 8601)
        return data.as_datetime().isoformat()
    elif isinstance(data, dict):
        # Se il dato è un dizionario, applica la conversione a ciascun valore
        return {key: convert_binary_to_base64(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Se il dato è una lista, applica la conversione a ciascun elemento
        return [convert_binary_to_base64(item) for item in data]
    else:
        # Se non è binario, Timestamp o bytes, restituisce il dato così com'è
        return data

# Connessione al database
client = MongoClient('mongodb://localhost:27141/')
db = client["Impianti_Fotovoltaici"]

# Recupera tutti i pannelli nella città di Avellino
pannelli = db.Pannelli.find({"Città": "Avellino"})

# Crea un dizionario per tenere traccia dei conteggi per ogni zona
zona_pannelli = {}

# Variabili per accumulare il totale dei documenti esaminati e il tempo impiegato
totale_docs_esaminati = 0
totale_tempo_esecuzione = 0

# Lista per raccogliere tutti gli explain per salvarli in un file
explain_results = []

# Iterazione attraverso tutti i pannelli
for pannello in pannelli:
    # Controllo in quale zona OMI si trova il pannello
    omi_zones = db.Avellino_OMI.find({
        "geometry": {
            "$geoIntersects": {
                "$geometry": pannello["location"]  # Verifica l'intersezione con il punto del pannello
            }
        }
    })

    # Explain per ottenere il piano di esecuzione della query
    explain_output = omi_zones.explain()

    # Conversione dei dati binari, bytes e Timestamp nell'explain in formato serializzabile
    explain_output_clean = convert_binary_to_base64(explain_output)

    # Aggiunta dell'explain serializzabile alla lista
    explain_results.append(explain_output_clean)

    # Accesso ai dati sulle performance della query
    execution_stats = explain_output.get('executionStats', {})
    docs_examined = execution_stats.get('totalDocsExamined', 0)  # Numero di documenti esaminati
    execution_time = execution_stats.get('executionTimeMillis', 0)  # Tempo di esecuzione in millisecondi

    # Somma dei valori per ottenere i totali
    totale_docs_esaminati += docs_examined
    totale_tempo_esecuzione += execution_time

    # Per ogni zona OMI trovata, viene incrementato il conteggio dei pannelli in quella zona
    for omi_zone in omi_zones:
        zona_name = omi_zone["properties"]["name"]
        if zona_name not in zona_pannelli:
            zona_pannelli[zona_name] = 0
        zona_pannelli[zona_name] += 1

# Stampa il totale dei documenti esaminati e il totale del tempo impiegato
print(f"Totale documenti esaminati: {totale_docs_esaminati}")
print(f"Totale tempo di esecuzione (ms): {totale_tempo_esecuzione}")

# Stampa il risultato: il conteggio dei pannelli per ciascuna zona
for zona_name, count in zona_pannelli.items():
    print(f"Zona OMI: {zona_name}, Numero di pannelli: {count}")

# Salva il risultato in un file CSV
with open('conteggio_pannelli_Avellino.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Zona OMI", "Numero di pannelli"])  # Intestazione del CSV
    for zona_name, count in zona_pannelli.items():
        writer.writerow([zona_name, count])

print("Risultato salvato.")

# Salva l'explain in un file JSON
with open('explain_results_query_pannelli.json', 'w', encoding='utf-8') as json_file:
    json.dump(explain_results, json_file, ensure_ascii=False, indent=4)

print("Dati dell'explain salvati.")
