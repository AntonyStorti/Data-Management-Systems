import csv
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
def create_spatial_nodes_and_relationships(session, csv_data, nome_città):
    layer_name = "stazioni_monitoraggio"
    # Crea il layer spaziale
    ensure_spatial_layer(session, layer_name) # Va commentato se il layer esiste già

    for row in csv_data:
        if row['COMUNE'] == nome_città:  # Filtra le stazioni per la città specifica
            name = row['Name']
            latitude = float(row['Latitudine'])
            longitude = float(row['Longitudine'])
            tipo_stazione = row['Tipo stazione']
            indirizzo = row['Indirizzo']
            altitudine = row['Altitudine']
            identificatore_sirav = row['Identificatore SIRAV']

            try:
                # Prima verifica se il nodo esiste
                result = session.run("""
                MATCH (s:StazioneMonitoraggio {name: $name, latitude: $latitude, longitude: $longitude})
                RETURN s
                """, name=name, latitude=latitude, longitude=longitude)

                # Se il nodo non esiste, lo crea
                if not result.peek():  # Verifica se non ci sono risultati
                    session.run("""
                    CREATE (s:StazioneMonitoraggio {
                        name: $name,
                        latitude: $latitude,
                        longitude: $longitude,
                        tipo_stazione: $tipo_stazione,
                        indirizzo: $indirizzo,
                        altitudine: $altitudine,
                        identificatore_sirav: $identificatore_sirav
                    })
                    """, name=name, latitude=latitude, longitude=longitude,
                                tipo_stazione=tipo_stazione, indirizzo=indirizzo, altitudine=altitudine,
                                identificatore_sirav=identificatore_sirav)

                    # Aggiunge il nodo al layer spaziale
                    session.run("""
                    MATCH (s:StazioneMonitoraggio {name: $name, latitude: $latitude, longitude: $longitude})
                    CALL spatial.addNode($layer_name, s) YIELD node
                    RETURN node
                    """, name=name, latitude=latitude, longitude=longitude,
                                tipo_stazione=tipo_stazione, indirizzo=indirizzo, altitudine=altitudine,
                                identificatore_sirav=identificatore_sirav, layer_name=layer_name)

                # Si assicura che il nodo per la città esista
                session.run("MERGE (c:Città {name: $città})", città=nome_città)

                # Creazione della relazione con la città specificata
                session.run("""
                MATCH (s:StazioneMonitoraggio {name: $name, latitude: $latitude, longitude: $longitude}),
                      (c:Città {name: $città})
                MERGE (c)-[:ha_stazione]->(s)
                """, name=name, latitude=latitude, longitude=longitude,
                            tipo_stazione=tipo_stazione, indirizzo=indirizzo, altitudine=altitudine,
                            identificatore_sirav=identificatore_sirav, città=nome_città)

            except Exception as e:
                print(f"Errore durante l'esecuzione delle query per {name}: {e}")


# Caricamento del file CSV
csv_data = []
try:
    with open('Stazioni Venezia.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Usa DictReader per leggere le righe come dizionari
        for row in reader:
            csv_data.append(row)
except Exception as e:
    print(f"Errore nella lettura del file CSV: {e}")
    driver.close()
    exit(1)

# Nome della città per associare le stazioni
nome_città = "Venezia"  # Modifica il nome della città qui

# Crea i nodi spaziali e le relazioni
with driver.session() as session:
    create_spatial_nodes_and_relationships(session, csv_data, nome_città)

# Chiude la connessione
driver.close()
