import base64
import csv
import json
from bson import Binary, Timestamp
from pymongo import MongoClient

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
        # Se non è binario, Timestamp o bytes, restituisci il dato così com'è
        return data

client = MongoClient('mongodb://localhost:27141/')
db = client["Impianti_Fotovoltaici"]

# Recupera tutti gli inquinanti nella città di Avellino
inquinanti = db.Inquinanti_Aria.find({"properties.COMUNE": "Avellino"})

# Crea un dizionario per tenere traccia degli inquinanti per ogni zona e dei loro valori
zona_inquinanti = {}

# Variabili per accumulare il totale dei documenti esaminati e il tempo impiegato
totale_docs_esaminati = 0
totale_tempo_esecuzione = 0

# Lista per raccogliere tutti gli explain per salvarli in un file
explain_results = []

# Iterazione attraverso tutti gli inquinanti
for inquinante in inquinanti:
    # Controllo in quale zona OMI si trova l'inquinante
    omi_zones = db.Avellino_OMI.find({
        "geometry": {
            "$geoIntersects": {
                "$geometry": inquinante["geometry"]  # Verifica l'intersezione con il punto dell'inquinante
            }
        }
    })

    # Esecuzione dell'explain per ottenere il piano di esecuzione della query
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

    # Per ogni zona OMI trovata, aggiunta del valore dell'inquinante (e somma dei valori)
    for omi_zone in omi_zones:
        zona_name = omi_zone["properties"]["name"]
        if zona_name not in zona_inquinanti:
            zona_inquinanti[zona_name] = {}  # Dizionario per contenere gli inquinanti per zona

        # Ottenimento del valore dell'inquinante e aggiornamento del dizionario
        inquinante_name = inquinante["properties"]["inquinante"]
        valore_inquinante = inquinante["properties"].get("valore", 0)

        if inquinante_name not in zona_inquinanti[zona_name]:
            zona_inquinanti[zona_name][inquinante_name] = []

        zona_inquinanti[zona_name][inquinante_name].append(valore_inquinante)

# Stampa il totale dei documenti esaminati e il totale del tempo impiegato
print(f"Totale documenti esaminati: {totale_docs_esaminati}")
print(f"Totale tempo di esecuzione (ms): {totale_tempo_esecuzione}")

# Calcolo della media dei valori per ogni inquinante in ogni zona
media_inquinanti_zona = {}

for zona_name, inquinanti_data in zona_inquinanti.items():
    media_inquinanti_zona[zona_name] = {}
    for inquinante_name, valori in inquinanti_data.items():
        media_inquinanti_zona[zona_name][inquinante_name] = sum(valori) / len(valori) if len(valori) > 0 else 0

# Stampa il risultato: la media dei valori per ciascun inquinante per zona
for zona_name, inquinanti in media_inquinanti_zona.items():
    print(f"Zona OMI: {zona_name}")
    for inquinante_name, media in inquinanti.items():
        print(f"  Inquinante: {inquinante_name}, Media: {media:.2f}")

# Salva il risultato in un file CSV con le medie
with open('media_inquinanti_Avellino.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Zona OMI", "Inquinante", "Media"])  # Intestazione del CSV
    for zona_name, inquinanti in media_inquinanti_zona.items():
        for inquinante_name, media in inquinanti.items():
            writer.writerow([zona_name, inquinante_name, f"{media:.2f}"])

print("Risultato delle medie salvato.")

# Salviamo l'explain in un file JSON
with open('explain_results_query_inquinanti_Avellino.json', 'w', encoding='utf-8') as json_file:
    json.dump(explain_results, json_file, ensure_ascii=False, indent=4)

print("Dati dell'explain salvati.")
