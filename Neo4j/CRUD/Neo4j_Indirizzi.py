import json
from neo4j import GraphDatabase

# Connessione al database Neo4j
uri = "bolt://localhost:7689"
username = "neo4j"
password = "***"

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
except Exception as e:
    print(f"Errore nella connessione a Neo4j: {e}")
    exit(1)

# Funzione per creare il layer spaziale
def ensure_spatial_layer(session, layer_name):
    result = session.run("CALL spatial.layers()")
    layers = [record["location"] for record in result]
    if layer_name not in layers:
        session.run("CALL spatial.addLayer($layer_name, 'SimplePoint', 'longitude:latitude')", layer_name=layer_name)

# Creazione di un vincolo di unicità per i nodi Indirizzo
def ensure_unique_constraint(session):
    try:
        session.run("""
        CREATE CONSTRAINT indirizzo_unico
        IF NOT EXISTS FOR (i:Indirizzo)
        REQUIRE (i.indirizzo, i.civico, i.longitude, i.latitude) IS UNIQUE
        """)
    except Exception as e:
        print(f"Errore nella creazione del vincolo di unicità: {e}")

# Funzione per creare nodi spaziali e relazioni
def create_spatial_nodes_and_relationships(json_data, nome_città):
    with driver.session() as session:
        # Crea il vincolo di unicità
        ensure_unique_constraint(session)

        # Crea il layer spaziale
        ensure_spatial_layer(session, "location") # Va commentato se esiste già

        for item in json_data:
            # Usa il nome della città passato come parametro
            if item.get("Città") == nome_città:  # Filtra gli indirizzi per la città specifica
                indirizzo = item.get("Indirizzo")
                civico = item.get("Civico")
                coordinates = item.get("location", {}).get("coordinates")

                if indirizzo and civico and isinstance(coordinates, list) and len(coordinates) == 2:
                    longitude, latitude = coordinates

                    try:
                        # Usa MERGE per garantire che il nodo sia unico
                        session.run("""
                        MERGE (i:Indirizzo {
                            indirizzo: $indirizzo,
                            civico: $civico,
                            longitude: $longitude,
                            latitude: $latitude
                        })
                        SET i.name = $name
                        """, indirizzo=indirizzo, civico=civico, longitude=longitude, latitude=latitude, name=f"{indirizzo}, {civico}")

                        # Aggiunta del nodo al layer spaziale
                        session.run("""
                        MATCH (i:Indirizzo {
                            indirizzo: $indirizzo,
                            civico: $civico,
                            longitude: $longitude,
                            latitude: $latitude
                        })
                        CALL spatial.addNode('location', i) YIELD node
                        RETURN node
                        """, indirizzo=indirizzo, civico=civico, longitude=longitude, latitude=latitude)

                        # Si assicura che il nodo per la città esista
                        session.run("MERGE (c:Città {name: $città})", città=nome_città)

                        # Creazione della relazione con la città specificata
                        session.run("""
                        MATCH (i:Indirizzo {
                            indirizzo: $indirizzo,
                            civico: $civico,
                            longitude: $longitude,
                            latitude: $latitude
                        }),
                              (c:Città {name: $città})
                        MERGE (c)-[:appartiene]->(i)
                        """, indirizzo=indirizzo, civico=civico, longitude=longitude, latitude=latitude, città=nome_città)
                    except Exception as e:
                        print(f"Errore durante l'esecuzione delle query per {indirizzo}, {civico}: {e}")

# Carica il file JSON
try:
    with open('Impianti_Fotovoltaici.Indirizzi.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Errore nella lettura del file JSON: {e}")
    driver.close()
    exit(1)

nome_città = "Avellino"

# Filtra i dati e crea i nodi e le relazioni per la città specificata
create_spatial_nodes_and_relationships(data, nome_città)

# Chiude la connessione
driver.close()
