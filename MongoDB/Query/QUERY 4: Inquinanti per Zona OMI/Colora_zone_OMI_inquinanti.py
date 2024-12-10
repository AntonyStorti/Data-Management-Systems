import random
import json
import numpy as np
import simplekml
from shapely.geometry import shape, MultiPolygon, Polygon
import zipfile
import os
import matplotlib.pyplot as plt
import csv
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


# Funzione per caricare il CSV con gli inquinanti per zona
def load_inquinanti_data(csv_file):
    zona_inquinanti = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Salta la riga di intestazione
        for row in reader:
            zona_name = row[0]
            inquinante = row[1]
            valore_inquinante = float(row[2])

            if zona_name not in zona_inquinanti:
                zona_inquinanti[zona_name] = []

            zona_inquinanti[zona_name].append(valore_inquinante)
    return zona_inquinanti


# Funzione per calcolare la media degli inquinanti per zona
def calcola_media_inquinanti(zona_inquinanti):
    zona_media_inquinanti = {}
    for zona, inquinanti in zona_inquinanti.items():
        zona_media_inquinanti[zona] = np.mean(inquinanti)
    return zona_media_inquinanti


# Percorso al file GeoJSON e CSV
geojson_file = 'AVELLINO.geojson'
csv_file = 'media_inquinanti_Avellino.csv'

# Carica il file GeoJSON
with open(geojson_file) as f:
    data = json.load(f)

# Carica i dati sugli inquinanti dal CSV
zona_inquinanti = load_inquinanti_data(csv_file)

# Calcola la media degli inquinanti per ogni zona
zona_media_inquinanti = calcola_media_inquinanti(zona_inquinanti)

# Crea un oggetto KML
kml = simplekml.Kml()

# Crea la figura per il plot
fig, ax = plt.subplots(figsize=(10, 10))

# Normalizzazione per mappare la media degli inquinanti su una scala di colori
min_inquinante = min(zona_media_inquinanti.values())
max_inquinante = max(zona_media_inquinanti.values())
norm = Normalize(vmin=min_inquinante, vmax=max_inquinante)
cmap = plt.get_cmap("plasma")
scalar_mappable = ScalarMappable(norm=norm, cmap=cmap)

# Colore grigio per le zone che non sono nel CSV
grigio = "#808080"

# Itera su ogni feature nel GeoJSON
for feature in data['features']:
    geom = shape(feature['geometry'])
    zona_name = feature['properties']['Name']

    # Se la zona è presente nei dati sugli inquinanti, prendi la media degli inquinanti, altrimenti usa il colore grigio
    media_inquinante = zona_media_inquinanti.get(zona_name, None)

    if media_inquinante is None:
        # Se la zona non è presente nel CSV, usa il colore grigio
        hex_color = grigio
    else:
        # Mappa la media degli inquinanti a un colore
        color = scalar_mappable.to_rgba(media_inquinante, bytes=True)  # Ottiene il colore dalla colormap
        hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])  # Converte in formato HEX

    # Determina se la geometria è un Poligono o MultiPoligono
    if isinstance(geom, Polygon):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = geom.geoms
    else:
        continue  # Salta altre tipologie di geometria

    # Itera su ciascun poligono
    for poly in polygons:
        # Estrae le coordinate esterne
        exterior_coords = list(poly.exterior.coords)

        # Crea il poligono nel KML
        pol = kml.newpolygon(name=zona_name, outerboundaryis=exterior_coords)

        # Imposta il colore di riempimento del poligono
        pol.style.polystyle.color = hex_color.replace('#', '')  # Rimuove il '#' e usa solo i valori RGB
        pol.style.polystyle.fill = 1  # Abilita il riempimento
        pol.style.polystyle.outline = 1  # Abilita il bordo

        # Imposta il contorno (bordo) nero
        pol.style.linestyle.color = 'ff000000'  # Contorno nero (4 caratteri: alpha + RGB)
        pol.style.linestyle.width = 2  # Larghezza del contorno

        # Gestisce eventuali "buchi" (interior rings)
        for interior in poly.interiors:
            interior_coords = list(interior.coords)
            pol.innerboundaryis = interior_coords  # Aggiunge il buco (se presente)

        # Aggiunge il poligono al plot
        exterior_coords = np.array(poly.exterior.coords)
        ax.fill(exterior_coords[:, 0], exterior_coords[:, 1], color=hex_color, edgecolor='black', linewidth=0.5)

        # Gestisce "buchi" nel plot
        for interior in poly.interiors:
            interior_coords = np.array(interior.coords)
            ax.fill(interior_coords[:, 0], interior_coords[:, 1], color='white', edgecolor='black', linewidth=0.5)

# Aggiunge un po' di padding ai limiti
minx, miny, maxx, maxy = ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1]
padding = 0.01
ax.set_xlim(minx - padding, maxx + padding)
ax.set_ylim(miny - padding, maxy + padding)

# Aggiunge titolo e etichette agli assi
plt.title('Mappa delle Zone OMI in Base alla Media degli Inquinanti')
ax.set_xlabel('Longitudine')
ax.set_ylabel('Latitudine')

# Imposta l'aspetto della mappa
ax.set_aspect('equal')

# Mostra la griglia
ax.grid(True, linestyle='--', alpha=0.5)

# Aggiunge la legenda
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Necessario per il corretto funzionamento della legenda
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Media Inquinanti')
cbar.set_ticks(np.linspace(min_inquinante, max_inquinante, num=5))

# Salva il grafico come PNG
plt.savefig('mappa_zone_colorata_Avellino_Inquinanti.png', bbox_inches='tight')

# Mostra il grafico
plt.show()

# Salva il KML su disco
kml_path = "output_media_Avellino.kml"
kml.save(kml_path)

# Comprime il KML in un file KMZ
kmz_path = "output_media_Avellino.kmz"
with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
    kmz.write(kml_path, os.path.basename(kml_path))

# Rimuove il file KML temporaneo
os.remove(kml_path)

print(f"File KMZ salvato come: {kmz_path}")
