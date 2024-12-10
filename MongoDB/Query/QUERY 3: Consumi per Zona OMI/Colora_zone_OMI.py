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


# Funzione per caricare il CSV con il consumo medio per zona
def load_consumi_data(csv_file):
    zona_consumi = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Salta la riga di intestazione
        for row in reader:
            zona_name = row[0]
            media_consumo = int(row[1])
            zona_consumi[zona_name] = media_consumo
    return zona_consumi


# Percorso al file GeoJSON e CSV
geojson_file = 'AVELLINO.geojson'
csv_file = 'risultato_query_Avellino_Consumi.csv'

# Carica il file GeoJSON
with open(geojson_file) as f:
    data = json.load(f)

# Carica i dati sui consumi dal CSV
zona_consumi = load_consumi_data(csv_file)

# Crea un oggetto KML
kml = simplekml.Kml()

# Crea la figura per il plot
fig, ax = plt.subplots(figsize=(10, 10))

# Normalizzazione per mappare il consumo medio su una scala di colori
min_consumi = min(zona_consumi.values())
max_consumi = max(zona_consumi.values())
norm = Normalize(vmin=min_consumi, vmax=max_consumi)
cmap = plt.get_cmap("plasma")
scalar_mappable = ScalarMappable(norm=norm, cmap=cmap)

# Itera su ogni feature nel GeoJSON
for feature in data['features']:
    geom = shape(feature['geometry'])
    zona_name = feature['properties']['Name']

    # Se la zona è presente nel CSV, prende il consumo medio, altrimenti usa 0
    med = zona_consumi.get(zona_name, 0)

    # Mappa il consumo medio a un colore
    color = scalar_mappable.to_rgba(media_consumo, bytes=True)  # Ottiene il colore dalla colormap
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
plt.title('Mappa delle Zone OMI in Base al Consumo Medio')
ax.set_xlabel('Longitudine')
ax.set_ylabel('Latitudine')

# Imposta l'aspetto della mappa
ax.set_aspect('equal')

# Mostra la griglia
ax.grid(True, linestyle='--', alpha=0.5)

# Aggiunge la legenda
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Necessario per il corretto funzionamento della legenda
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Consumo Medio')
cbar.set_ticks(np.linspace(min_consumi, max_consumi, num=5))

# Salva il grafico come PNG
plt.savefig('mappa_zone_colorata_Avellino_Consumi.png', bbox_inches='tight')

# Mostra il grafico
plt.show()

# Salva il KML su disco
kml_path = "output_colorato_Avellino.kml"
kml.save(kml_path)

# Comprime il KML in un file KMZ
kmz_path = "output_colorato_Avellino.kmz"
with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
    kmz.write(kml_path, os.path.basename(kml_path))

# Rimuove il file KML temporaneo
os.remove(kml_path)

print(f"File KMZ salvato come: {kmz_path}")
