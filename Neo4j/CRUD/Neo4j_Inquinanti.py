import json
from neo4j import GraphDatabase
from datetime import datetime

# Connessione a Neo4j
uri = "bolt://localhost:7689"
username = "neo4j"
password = "crociera"

# Inizializza il driver di Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))


# Funzione per leggere e filtrare il file JSON
def read_and_filter_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Filtra i dati per COMUNE == 'Avellino'
    filtered_data = [entry for entry in data if entry.get('properties', {}).get('COMUNE') == 'Avellino']

    return filtered_data


# Funzione per eseguire il merge dei nodi e creare l'arco in Neo4j
def process_data(driver, json_data):
    with driver.session() as session:
        for entry in json_data:
            # Estrae i dati dal JSON
            properties = entry.get('properties', {})
            name = properties.get('Name')  # Nome della stazione di monitoraggio
            inquinante = properties.get('inquinante')  # Nome dell'inquinante
            valore = properties.get('valore')  # Valore dell'inquinante
            um = properties.get('um')  # Unità di misura
            data_ora = properties.get('data_ora')  # Data e ora

            # Aggiunge un controllo per assicurarsi che data_ora sia un dizionario con chiave "$date"
            if isinstance(data_ora, dict) and "$date" in data_ora:
                data_ora = data_ora["$date"]  # Estrae la data dalla chiave "$date"
            else:
                print(f"Data ora mancante o in formato errato per {name}, {inquinante}")
                continue  # Salta questa iterazione se la data è mancante o mal formata

            # Converte data_ora (ISO 8601) in formato DateTime di Neo4j
            try:
                data_ora = datetime.strptime(data_ora, "%Y-%m-%dT%H:%M:%S.%fZ")  # ISO 8601
            except ValueError:
                print(f"Errore nel formato della data per {name}, {inquinante}. Data: {data_ora}")
                continue  # Se il formato della data è errato, salta questa iterazione

            # Esegue il MERGE del nodo Inquinante, includendo anche la data_ora e name della stazione
            session.run("""
                MERGE (i:Inquinante {name: $inquinante, data_ora: $data_ora, stazione_name: $stazione_name})
                """, inquinante=inquinante, data_ora=data_ora, stazione_name=name)

            # Crea il collegamento tra la StazioneMonitoraggio e l'Inquinante
            session.run("""
                MATCH (s:StazioneMonitoraggio {name: $name})
                MATCH (i:Inquinante {name: $inquinante, data_ora: $data_ora, stazione_name: $stazione_name})
                MERGE (s)-[r:ha_monitorato]->(i)
                SET r.valore = $valore,
                    r.um = $um
                """, name=name, inquinante=inquinante, valore=valore, um=um, data_ora=data_ora, stazione_name=name)


# Main function
def main():
    file_path = 'Impianti_Fotovoltaici.Inquinanti_Aria.json'
    json_data = read_and_filter_json(file_path)

    if json_data:
        process_data(driver, json_data)
    else:
        print("Nessun dato trovato per il dato comune.")


# Esegui lo script
if __name__ == "__main__":
    main()
