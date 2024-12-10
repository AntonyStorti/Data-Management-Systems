from datetime import datetime
from neo4j import GraphDatabase
import json

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def process_data(self, indirizzi_json, persone_json):
        total_soggetti = sum(len(indirizzo_entry.get("Soggetto", [])) for indirizzo_entry in indirizzi_json)  # Calcola il totale
        soggetti_inserted = 0  # Contatore per i soggetti inseriti

        with self.driver.session() as session:
            for indirizzo_entry in indirizzi_json:
                indirizzo = indirizzo_entry.get("Indirizzo")
                civico = indirizzo_entry.get("Civico")
                coordinates = indirizzo_entry.get("location", {}).get("coordinates")
                soggetti_ids = indirizzo_entry.get("Soggetto", [])

                indirizzo_node_id = session.execute_write(
                    self.get_or_create_indirizzo, indirizzo, civico, coordinates
                )

                # Conta e stampa il numero di soggetti che verranno aggiunti
                # num_soggetti = len(soggetti_ids)
                # print(f"Numero di soggetti da aggiungere per l'indirizzo {indirizzo} {civico}: {num_soggetti}")

                for soggetto_id in soggetti_ids:
                    soggetto_id_str = soggetto_id["$oid"]

                    # Trova la persona basandosi sull'ObjectId, ma non lo usa nel nodo
                    persona = next(
                        (p for p in persone_json if p["_id"]["$oid"] == soggetto_id_str),
                        None
                    )

                    if persona:
                        try:
                            session.execute_write(
                                self.create_soggetto_and_relationship,
                                indirizzo_node_id,
                                persona  # Passa solo i dati della persona
                            )
                            soggetti_inserted += 1  # Aumenta il contatore dei soggetti inseriti
                            print(f"Inserito soggetto {soggetti_inserted}/{total_soggetti}")  # Stampa lo stato di avanzamento
                        except Exception as e:
                            print(f"Errore nell'inserimento di soggetto {soggetto_id_str} per l'indirizzo {indirizzo} {civico}: {e}")
                    else:
                        print(f"Persona non trovata per Soggetto ID {soggetto_id_str} nell'indirizzo {indirizzo} {civico}")

    @staticmethod
    def process_date(date_field):
        if isinstance(date_field, dict) and "$date" in date_field:
            # Controlla se il valore è un oggetto complesso con un timestamp
            if isinstance(date_field["$date"], dict) and "$numberLong" in date_field["$date"]:
                try:
                    # Converte il valore in un intero timestamp
                    timestamp = int(date_field["$date"]["$numberLong"])
                    # Converte il timestamp in un formato DATE (yyyy-mm-dd)
                    return datetime.utcfromtimestamp(
                        timestamp / 1000).date()  # Usa .date() per ottenere solo la parte data
                except ValueError:
                    pass
            # Se $date è già una stringa in formato ISO 8601, estrae la parte della data
            date_str = str(date_field["$date"])
            if "T" in date_str:
                date_str = date_str.split("T")[0]  # Estrae solo la parte della data
            return datetime.strptime(date_str, "%Y-%m-%d").date()  # Restituisce un oggetto date
        return None  # Ritorna None se non è un campo valido

    @staticmethod
    def get_or_create_indirizzo(tx, indirizzo, civico, coordinates):
        longitude, latitude = coordinates
        query = """
        MERGE (i:Indirizzo {indirizzo: $indirizzo, civico: $civico, longitude: $longitude, latitude: $latitude})
        RETURN i
        """
        result = tx.run(query, indirizzo=indirizzo, civico=civico, longitude=longitude, latitude=latitude)
        return result.single()["i"]

    @staticmethod
    def create_soggetto_and_relationship(tx, indirizzo_node, persona):
        query = """
        MERGE (s:Soggetto {name: $name, data_nascita: $data_nascita, reddito_imponibile: $reddito_imponibile})
        ON CREATE SET s.categoria_reddito = $categoria_reddito,
                      s.codice_attivita = $codice_attivita,
                      s.imposta_netta = $imposta_netta,
                      s.reddito_impresa = $reddito_impresa,
                      s.volume_affari = $volume_affari,
                      s.tipo_modello = $tipo_modello
        WITH s
        MATCH (i:Indirizzo {indirizzo: $indirizzo, civico: $civico, longitude: $longitude, latitude: $latitude})
        MERGE (i)-[:residenza_di]->(s)
        """
        tx.run(
            query,
            indirizzo=indirizzo_node["indirizzo"],
            civico=indirizzo_node["civico"],
            longitude=indirizzo_node["longitude"],
            latitude=indirizzo_node["latitude"],
            name=persona.get("Soggetto"),
            data_nascita=Neo4jHandler.process_date(persona.get("Data di Nascita")),
            reddito_imponibile=persona.get("Reddito Imponibile"),
            categoria_reddito=persona.get("Categoria di Reddito"),
            codice_attivita=persona.get("Codice Attività"),
            imposta_netta=persona.get("Imposta Netta"),
            reddito_impresa=persona.get("Reddito d'Impresa / Lavoro Autonomo"),
            volume_affari=persona.get("Volume d'Affari"),
            tipo_modello=persona.get("Tipo Modello"),
        )


neo4j_uri = "bolt://localhost:7689"
neo4j_user = "neo4j"
neo4j_password = "***"
indirizzi_file = "Impianti_Fotovoltaici.Indirizzi.json"
persone_file = "Impianti_Fotovoltaici.Avellino_Redditi.json"

# Carica i dati JSON
with open(indirizzi_file, "r", encoding="utf-8") as f:
    indirizzi_data = json.load(f)

with open(persone_file, "r", encoding="utf-8") as f:
    persone_data = json.load(f)

# Filtra solo gli indirizzi con Città "Avellino"
indirizzi_data_avellino = [
    indirizzo for indirizzo in indirizzi_data if indirizzo.get("Città") == "Avellino"
]

# Esegue lo script
handler = Neo4jHandler(neo4j_uri, neo4j_user, neo4j_password)
try:
    handler.process_data(indirizzi_data_avellino, persone_data)
finally:
    handler.close()

print("Elaborazione completata.")
