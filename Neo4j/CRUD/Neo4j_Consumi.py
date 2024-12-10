import json
from neo4j import GraphDatabase
from datetime import datetime


# Funzione per connettersi a Neo4j
def get_neo4j_driver(uri, user, password):
    return GraphDatabase.driver(uri, auth=(user, password))


# Funzione per creare i nodi e gli archi
def process_json_and_create_nodes_and_relationships(driver, json_data):
    with driver.session() as session:
        for record in json_data:
            città = record["città"]

            # Filtra solo i record con città = "Avellino"
            if città == "Avellino":
                codzona = record["codzona"]
                consumo_energetico = record["consumo_energetico"]
                unita_misura = record["Unità Misura"]
                data_ora = record["data_ora"]["$date"]

                # Parsing della data in formato datetime di Python
                data_ora = datetime.strptime(data_ora, "%Y-%m-%dT%H:%M:%S.%fZ")

                # Formattazione della data in un formato compatibile con Neo4j
                data_ora_neo4j = data_ora.isoformat()  # formato YYYY-MM-DDTHH:MM:SS.sss

                # Creazione nodo per la zona
                query = f"""
                MERGE (z:Feature {{CODCOM: 'L736', CODZONA: '{codzona}'}})

                MERGE (c:Consumo {{codcom: 'L736', codzona: '{codzona}', data_ora: datetime('{data_ora_neo4j}')}})

                MERGE (z)-[r:ha_consumo {{consumo_energetico: {consumo_energetico}, unita_misura: '{unita_misura}'}}]->(c)
                """
                session.run(query)


# Funzione principale per leggere il JSON e processarlo
def main():
    # Carica il file JSON
    with open('Impianti_Fotovoltaici.Consumi_Elettrici.json', 'r') as f:
        json_data = json.load(f)

    # Connessione a Neo4j
    uri = "bolt://localhost:7689"
    user = "neo4j"
    password = "***"

    driver = get_neo4j_driver(uri, user, password)

    # Processa i dati e crea nodi e archi
    process_json_and_create_nodes_and_relationships(driver, json_data)

    # Chiude la connessione
    driver.close()


# Esegui lo script
if __name__ == "__main__":
    main()
