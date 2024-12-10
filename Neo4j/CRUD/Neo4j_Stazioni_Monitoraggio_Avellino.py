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
    session.run("CALL spatial.addLayer($layer_name, 'SimplePoint', 'longitude:latitude')", layer_name=layer_name)


# Funzione per creare un vincolo di unicità per i nodi StazioneMonitoraggio
def ensure_unique_constraint(session):
    try:
        session.run("""
        CREATE CONSTRAINT stazione_unica
        IF NOT EXISTS FOR (s:StazioneMonitoraggio)
        REQUIRE (s.name, s.latitude, s.longitude) IS UNIQUE
        """)
    except Exception as e:
        print(f"Errore nella creazione del vincolo di unicità: {e}")

# Funzione per creare nodi spaziali e relazioni
def create_spatial_nodes_and_relationships(session, geojson_data, nome_città):
    layer_name = "stazioni_monitoraggio"
    # Crea il layer spaziale
    ensure_spatial_layer(session, layer_name) # Va commentato se esiste già

    for feature in geojson_data['features']:
        properties = feature['properties']
        geometry = feature['geometry']

        if properties['COMUNE'] == nome_città:  # Filtra le stazioni per la città specifica
            name = properties['Name']
            latitude = properties['LAT']
            longitude = properties['LONG']
            zone_code = properties['ZONE_CODE']
            zona = properties['ZONA']
            stazione = properties['STAZIONE']
            ubicazione = properties['UBICAZIONE']
            gestione = properties['GESTIONE']

            try:
                # Usa MERGE per garantire che il nodo sia unico
                session.run("""
                MERGE (s:StazioneMonitoraggio {
                    name: $name,
                    latitude: $latitude,
                    longitude: $longitude,
                    zone_code: $zone_code,
                    zona: $zona,
                    stazione: $stazione,
                    ubicazione: $ubicazione,
                    gestione: $gestione
                })
                SET s.name = $name
                """, name=name, latitude=latitude, longitude=longitude,
                    zone_code=zone_code, zona=zona, stazione=stazione,
                    ubicazione=ubicazione, gestione=gestione)

                # Aggiunta del nodo al layer spaziale
                session.run("""
                MATCH (s:StazioneMonitoraggio {
                    name: $name,
                    latitude: $latitude,
                    longitude: $longitude,
                    zone_code: $zone_code,
                    zona: $zona,
                    stazione: $stazione,
                    ubicazione: $ubicazione,
                    gestione: $gestione
                })
                CALL spatial.addNode($layer_name, s) YIELD node
                RETURN node
                """, name=name, latitude=latitude, longitude=longitude,
                    zone_code=zone_code, zona=zona, stazione=stazione,
                    ubicazione=ubicazione, gestione=gestione, layer_name=layer_name)

                # Si assicura che il nodo per la città esista
                session.run("MERGE (c:Città {name: $città})", città=nome_città)

                # Creazione della relazione con la città specificata
                session.run("""
                MATCH (s:StazioneMonitoraggio {
                    name: $name,
                    latitude: $latitude,
                    longitude: $longitude,
                    zone_code: $zone_code,
                    zona: $zona,
                    stazione: $stazione,
                    ubicazione: $ubicazione,
                    gestione: $gestione
                }),
                      (c:Città {name: $città})
                MERGE (c)-[:ha_stazione]->(s)
                """, name=name, latitude=latitude, longitude=longitude,
                    zone_code=zone_code, zona=zona, stazione=stazione,
                    ubicazione=ubicazione, gestione=gestione, città=nome_città)

            except Exception as e:
                print(f"Errore durante l'esecuzione delle query per {name}: {e}")

# Caricamento del file GeoJSON
try:
    with open('Stazioni Campania.geojson', 'r') as f:
        geojson_data = json.load(f)
except Exception as e:
    print(f"Errore nella lettura del file GeoJSON: {e}")
    driver.close()
    exit(1)

# Nome della città per associare le stazioni
nome_città = "Avellino"

# Crea i nodi spaziali e le relazioni
with driver.session() as session:
    create_spatial_nodes_and_relationships(session, geojson_data, nome_città)

# Chiude la connessione
driver.close()
