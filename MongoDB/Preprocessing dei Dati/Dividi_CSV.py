import csv

def split_csv(input_file, output_prefix, rows_per_file=100001):
    # Legge il file CSV originale
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Prende l'intestazione

        # Inizializza le variabili
        current_rows = []
        file_count = 1

        # Aggiunge l'intestazione alla prima parte
        current_rows.append(header)

        # Legge tutte le righe del file CSV e le divide
        for row_number, row in enumerate(reader, start=1):
            current_rows.append(row)

            # Quando si raggiungono 100.000 righe di dati (101.001 comprese intestazione)
            if len(current_rows) == rows_per_file:
                output_file = f"{output_prefix}_{file_count}.csv"
                with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows(current_rows)
                print(f"File {output_file} creato.")
                file_count += 1
                current_rows = [header]  # Riparte con l'intestazione per il prossimo file

        # Gestisce l'ultimo file che potrebbe essere parziale
        if current_rows != [header]:  # Se ci sono righe residue
            output_file = f"{output_prefix}_{file_count}.csv"
            with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(current_rows)
            print(f"File {output_file} creato.")


input_file = './Milano/Milano_Consumi.csv'  # Sostituisci con il tuo file
output_prefix = './Consumi_Milano/Milano-'   # Prefisso per i file di output
split_csv(input_file, output_prefix)
