import json
from neo4j import GraphDatabase
from shapely.geometry import shape
from shapely import wkt

# Configura la connessione a Neo4j
uri = "bolt://localhost:7689"
user = "neo4j"
password = "***"

# Crea una sessione con Neo4j
driver = GraphDatabase.driver(uri, auth=(user, password))
session = driver.session()

# Funzione per creare il layer spaziale in Neo4j
def create_spatial_layer():
    session.run("CALL spatial.addLayer('zone_omi', 'wkt', '')")

# Funzione per creare il nodo Città se non esiste
def create_city_node(city_name):
    session.run("MERGE (c:Città {name: $city_name})", city_name=city_name)

# Funzione per aggiungere i poligoni/multipoligoni e le proprietà al database
def add_features_to_neo4j(geojson_file):
    with open(geojson_file) as f:
        data = json.load(f)

    for feature in data['features']:
        # Estrae il nome, la descrizione e altre proprietà
        feature_name = feature['properties']['Name']
        description = feature['properties']['description']
        codcom = feature['properties']['CODCOM']
        codzona = feature['properties']['CODZONA']

        # Estrae la geometria (poligono o multipoligono)
        geometry = feature['geometry']
        geometry_type = geometry['type']
        coordinates = geometry['coordinates']

        # Usa shapely per convertire la geometria in WKT
        shapely_geom = shape(geometry)
        wkt_geometry = shapely_geom.wkt

        # Crea un nodo per la feature e lo collega al nodo "Città" con nome "Avellino"
        session.run("""
            MERGE (c:Città {name: 'Avellino'})
            MERGE (f:Feature {name: $feature_name, description: $description, CODCOM: $codcom, CODZONA: $codzona, geometry: $wkt_geometry})
            MERGE (c)-[:divisa_in]->(f)
            WITH f
            CALL spatial.addNode('zone_omi', f) YIELD node RETURN node
        """, feature_name=feature_name, description=description, codcom=codcom, codzona=codzona,
                    wkt_geometry=wkt_geometry)

# Creazione del layer spaziale e dei nodi
create_spatial_layer() # Va commentato se il layer esiste già
create_city_node('Avellino')

# Aggiunge le feature dal file GeoJSON
geojson_file = 'AVELLINO.geojson'
add_features_to_neo4j(geojson_file)

# Chiude la sessione
session.close()
driver.close()
