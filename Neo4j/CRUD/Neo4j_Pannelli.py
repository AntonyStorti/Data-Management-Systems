import json
from neo4j import GraphDatabase

# Configurazione del database
NEO4J_URI = "bolt://localhost:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "crociera"

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_pannello_node(self):
        with self.driver.session() as session:
            session.run("MERGE (p:Pannello {name: 'Pannello'})")

    def create_address_relationships(self, json_data):
        with self.driver.session() as session:
            for item in json_data:
                # Filtra per città = Avellino
                if item.get("Città") != "Venezia":
                    continue

                indirizzo = item.get("Indirizzo")
                civico = item.get("Civico")
                longitude, latitude = item["location"]["coordinates"]

                # Effettua il match per il nodo Indirizzo e crea la relazione con Pannello
                session.run(
                    """
                    MATCH (a:Indirizzo {indirizzo: $indirizzo, civico: $civico, longitude: $longitude, latitude: $latitude})
                    MATCH (p:Pannello {name: 'Pannello'})
                    MERGE (a)-[:ha]->(p)
                    """,
                    indirizzo=indirizzo,
                    civico=civico,
                    longitude=longitude,
                    latitude=latitude
                )

# Funzione principale
def main():
    # Percorso al file JSON
    json_file_path = "Impianti_Fotovoltaici.Pannelli.json"

    # Caricamento dati JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Connessione al database Neo4j
    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # Creazione del nodo Pannello
        neo4j_handler.create_pannello_node()

        # Creazione delle relazioni tra Indirizzo e Pannello
        neo4j_handler.create_address_relationships(json_data)
    finally:
        # Chiusura connessione
        neo4j_handler.close()

if __name__ == "__main__":
    main()
