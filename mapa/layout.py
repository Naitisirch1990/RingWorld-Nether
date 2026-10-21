"""Layout del Nether independiente. Circunferencia 14976, ancho 1008."""
import csv
import json
from pathlib import Path
LENGTH=14976
WIDTH=1008
SECTOR=2496
SPAWN=(142,84,0)
BIOMES=['minecraft:nether_wastes','minecraft:crimson_forest','minecraft:warped_forest','minecraft:soul_sand_valley','minecraft:basalt_deltas','minecraft:nether_wastes']
NAMES=['Spawn de cenizas','Ciudad carmesí','Bosque distorsionado','Valle de almas','Región volcánica','Fortaleza final']
DATA=[
(1,'principal','Spawn del Nether','spawn_598869.schematic',142,0),
(1,'secundaria','Portal de vigilancia',None,612,240),
(1,'natural','Portal en ruinas',None,14558,275),
(1,'natural','Santuario de magma',None,882,-300),
(2,'principal','Ciudad carmesí',None,2638,-210),
(2,'secundaria','Santuario carmesí',None,3108,240),
(2,'natural','Bastión de piglins',None,2078,275),
(2,'natural','Jardín de hongos',None,3378,-300),
(3,'principal','Templo distorsionado','themawofthenether.schem',5134,-210),
(3,'secundaria','Observatorio distorsionado',None,5604,240),
(3,'natural','Bosque de hongos antiguos',None,4574,275),
(3,'natural','Ruinas distorsionadas',None,5874,-300),
(4,'principal','Arena de almas','nether-pvp-arena1.schem',7630,-210),
(4,'secundaria','Catacumbas de almas',None,8100,240),
(4,'natural','Fósil gigante',None,7070,275),
(4,'natural','Foso de fuego azul',None,8370,-300),
(5,'principal','Ciudad volcánica',None,10126,-210),
(5,'secundaria','Forja de basaltos',None,10596,240),
(5,'natural','Volcán gigante',None,9566,275),
(5,'natural','Grieta de lava',None,10866,-300),
(6,'principal','Fortaleza de las cenizas',None,12622,-210),
(6,'secundaria','Bastión final',None,13092,240),
(6,'natural','Bastión de hoglins',None,12062,275),
(6,'natural','Fortaleza antigua','Nether Bridge Design 2.litematic',13362,-300),
]
STRUCTURES=[dict(id=f's{i:02d}',sector=s,type=t,name=n,source=src,x=x,z=z,loot_chests=10) for i,(s,t,n,src,x,z) in enumerate(DATA,1)]
assert len(STRUCTURES)==24
def write_plan(directory):
    p=Path(directory);p.mkdir(parents=True,exist_ok=True)
    (p/'plano.json').write_text(json.dumps(dict(length=LENGTH,width=WIDTH,sector_length=SECTOR,spawn={'x':142,'y':84,'z':0},biomes=BIOMES,structures=STRUCTURES,road={'z':0,'width':7,'clearance':5,'lighting_interval':12}),ensure_ascii=False,indent=2),encoding='utf8')
    with (p/'estructuras.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=STRUCTURES[0]);w.writeheader();w.writerows(STRUCTURES)
