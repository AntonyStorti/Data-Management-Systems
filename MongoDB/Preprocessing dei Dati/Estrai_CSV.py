import csv
import re
import os


input_folder = './Genova'
output_file = './Genova/Genova.csv'

# Funzione per pulire e formattare i dati
def parse_line(line):
    # Usa una regex per catturare i vari campi
    pattern = r'^(.*?)\s+(\d{4}-\d{2}-\d{2})\s+(\S+)?\s*(\S+)?\s*([0-9.]+(?:,[0-9]+)?)\s+([0-9.]+(?:,[0-9]+)?)\s+([0-9.]+(?:,[0-9]+)?)\s+([0-9.]+(?:,[0-9]+)?)\s+(.*)$'
    match = re.match(pattern, line)
    if match:
        parsed_data = list(match.groups())
        # Converte i valori monetari da stringa a float
        for i in range(4, 8):  # Indici delle colonne con valori monetari
            if parsed_data[i]:  # Si assicura che il campo non sia vuoto
                # Sostituisce il punto con nulla e la virgola con un punto
                parsed_data[i] = float(parsed_data[i].replace('.', '').replace(',', '.'))
        return parsed_data
    return None

# Apre il file CSV di output
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)

    # Scrive l'intestazione nel file CSV
    writer.writerow(['Soggetto', 'Data di Nascita', 'Categoria di Reddito', 'Codice Attività',
                     'Reddito Imponibile', 'Imposta Netta', 'Reddito d\'Impresa / Lavoro Autonomo',
                     'Volume d\'Affari', 'Tipo Modello', 'Indirizzo'])

    # Elenca tutti i file .txt nella cartella specificata
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            try:
                # Apre ogni file di input
                with open(file_path, 'r', encoding='utf-8') as infile:
                    # Legge ogni riga dal file di input
                    for line_number, line in enumerate(infile, start=1):
                        line = line.strip()  # Rimuove eventuali spazi vuoti all'inizio e alla fine
                        if line:  # Si assicura che la linea non sia vuota
                            try:
                                parsed_data = parse_line(line)
                                if parsed_data:
                                    writer.writerow(parsed_data)
                            except ValueError as ve:
                                # Stampa un messaggio d'errore con dettagli sul file e la riga che ha causato il problema
                                print(f"Errore nella conversione del file {filename}, riga {line_number}: {line}")
                                print(f"Dettagli dell'errore: {ve}")
            except Exception as e:
                # Gestione dell'errore per problemi legati all'apertura del file
                print(f"Errore nell'elaborazione del file {filename}: {e}")

print(f'Conversione completata! I dati sono stati salvati in {output_file}.')
