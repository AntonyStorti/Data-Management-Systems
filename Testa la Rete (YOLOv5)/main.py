import torch

# Carica il modello (assicurati di sostituire 'path_to_model' con il percorso corretto)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='Modelli Addestrati/object_detection_models/yolov5_X.pt')  # Carica il modello personalizzato

# Esegui una previsione su un'immagine (sostituisci 'image.jpg' con il tuo file immagine)
img = 'Schermata2.png'  # Può essere un file immagine, un array numpy, o una lista di immagini
results = model(img)

# Mostra i risultati
results.show()  # Mostra l'immagine con le previsioni
results.print()  # Stampa le etichette, la confidenza e le coordinate dei bounding box
