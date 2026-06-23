# Génère catalog.js (catalogue structuré pour l'éditeur) à partir des PNG.
# Regroupement automatique par nom de fichier.
import os, re, json, glob
from collections import defaultdict, OrderedDict
from PIL import Image

ROOT = 'assets/tiles'

def cat_of(p):
    pl = p.replace(os.sep, '/')
    if 'Hex Basic Set' in pl: return 'basic'
    if '/Decor/' in pl: return 'decor'
    if '/Tiles/' in pl: return 'composite'
    if '/Base Tiles/' in pl: return 'base'
    if '/Roads/' in pl: return 'roads'
    return None

def dims(p):
    try:
        return Image.open(p).size
    except Exception:
        return (0, 0)

# stem = nom sans digits/suffixe de couleur final -> regroupe les variantes
def stem_of(name):
    return re.sub(r'(\d+)(_[a-zA-Z]+)?$', '', name)

# ---- biomes (tokens longest-first -> groupe d'affichage) ----
BIOME_TOKENS = [
    ('ForestBroadleaf','Forest'),('ForestPineSnowCovered','Forest'),('ForestPine','Forest'),
    ('ForestBurned','Forest'),('Forest','Forest'),('Woodlands','Forest'),
    ('Jungle','Jungle'),
    ('PlainsColdSnowTransition','Plains'),('PlainsCold','Plains'),('PlainsFarm','Plains'),('Plains','Plains'),
    ('Highlands','Hills'),('Hills','Hills'),
    ('MountainSnow','Mountains'),('Mountain','Mountains'),
    ('DesertDunesOasis','Desert'),('DesertDunes','Desert'),('DesertRedMountains','Desert'),
    ('DesertRedForest','Desert'),('DesertRedDirt','Desert'),('DesertYellowCactiForest','Desert'),
    ('DesertYellowMesaLarge','Desert'),('DesertYellowHills','Desert'),('DesertRed','Desert'),
    ('DesertYellow','Desert'),('Desert','Desert'),('SandPalms','Desert'),
    ('Marsh','Marsh'),('Swamp','Swamp'),('Wetlands','Marsh'),
    ('SnowField','Snow'),
    ('Scrublands','Scrublands'),
    ('LavaField','Volcanic'),('VolcanoActive','Volcanic'),('AshPlains','Volcanic'),('Volcano','Volcanic'),
    ('OceanCalm','Eaux'),('Ocean','Eaux'),
    ('UnderOcean','Souterrain'),('UnderVoid','Souterrain'),('UnderDirt','Souterrain'),
    ('Undercliff','Souterrain'),('Void','Souterrain'),
    ('Dirt','Terre'),
    ('Base','Base'),
]
BIOME_ORDER = ['Plains','Forest','Jungle','Hills','Mountains','Desert','Marsh','Swamp',
               'Snow','Scrublands','Volcanic','Eaux','Terre','Souterrain','Base','Autres']

def split_words(s):
    s = re.sub(r'(\d+)(_[a-zA-Z]+)?$', '', s)
    s = s.replace('_', ' ')
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    return s.strip().title()

def biome_of(stem):
    # stem commence par "hex"
    body = stem[3:] if stem.startswith('hex') else stem
    for tok, grp in BIOME_TOKENS:
        if body.startswith(tok):
            feature = body[len(tok):]
            return grp, tok, feature
    return 'Autres', '', body

# ---- objets : catégorisation par mots-clés ----
OBJ_CATS = [
    ('Nature', ['tree','trees','bush','shrub','mushroom','cloud','mist','rock','rocks','outcrop',
                'boulder','decormountain','pond','lake','oasis','iceberg','palm','cactus','crystal',
                'waterfall','flower','redrock','lavarocks','spring']),
    ('Bâtiments', ['house','hut','cabin','lodge','cottage','tower','church','temple','chapel','shrine',
                   'inn','smithy','barracks','fortress','keep','manor','mansion','dwarf','elven','elf',
                   'halfling','yurt','longhouse','tent','scriptorium','adobe','round','thatched','wood',
                   'necro','stronghold','wizard']),
    ('Peuplements', ['village','town','city','hamlet','walledcity','settlement']),
    ('Industrie', ['mill','windmill','mine','mines','quarry','claypit','logging','warehouse','kiln',
                   'forge','slavers','toll','cattle','caravanserai','clay']),
    ('Agriculture', ['farm','field','barn','granary','haystack','silo','corral','pasture','pen',
                     'chicken','flock','herd','crop','swidden','orchard','scarecrow','straw','cookhouse',
                     'well','cows','pigs','sheep','meadow','felled']),
    ('Militaire', ['archery','battlefield','checkpoint','prisoner','trench','warmonument','statue',
                   'banditcamp','bandit','tourney','ambush','massgrave','war']),
    ('Mystère & Ruines', ['ruin','ruins','barrow','tomb','graveyard','cemetery','dolmen','standing',
                          'henge','obelisk','idol','totem','calvary','cross','vault','desecrated',
                          'gallows','bones','skull','sphinx','pyramid','ziggurat','masks']),
    ('Voyage', ['bridge','sign','boardwalk','stairs','zipline','boundary','ledge','road','path']),
    ('Magie', ['portal','teleport','magic','mana','beacon','rune','altar','circle']),
]
def obj_cat(name):
    n = name.lower()
    for cat, kws in OBJ_CATS:
        for kw in kws:
            if kw in n:
                return cat
    return 'Divers'

# ============ scan ============
files = []
for p in glob.glob(os.path.join(ROOT, '**', '*.png'), recursive=True):
    c = cat_of(p)
    if c is None: continue
    w, h = dims(p)
    files.append({'p': p.replace(os.sep,'/'), 'n': os.path.basename(p)[:-4], 'c': c, 'w': w, 'h': h})

# ---- regrouper en items (variantes) par (catégorie-source, stem) ----
def build_items(file_list):
    groups = defaultdict(list)
    for f in file_list:
        groups[stem_of(f['n'])].append(f)
    items = []
    for stem, fs in groups.items():
        fs.sort(key=lambda x: x['n'])
        w, h = fs[0]['w'], fs[0]['h']
        items.append({'id': stem, 'variants': [f['p'] for f in fs], 'w': w, 'h': h, 'sample': fs})
    return items

# ===== TILES =====
# base terrains = basic (hex* plein hex) + base ; composites = Locations/Tiles
base_files_all = [f for f in files if (f['c']=='basic' and f['n'].startswith('hex') and f['w']==256 and f['h']==384) or f['c']=='base']
composite_files_all = [f for f in files if f['c']=='composite']

# une tuile "à feature" (ex. hexPlainsFarm) présente côté basic doit rejoindre les composites,
# pas la section Terrain. On route par "stem présent côté composite".
composite_stems = set(stem_of(f['n']) for f in composite_files_all)
base_files = [f for f in base_files_all if stem_of(f['n']) not in composite_stems]
composite_files = composite_files_all + [f for f in base_files_all if stem_of(f['n']) in composite_stems]

terrain_items = []
for it in build_items(base_files):
    grp, tok, feat = biome_of(it['id'])
    terrain_items.append({'id': it['id'], 'name': split_words(it['id'][3:] if it['id'].startswith('hex') else it['id']),
                          'variants': it['variants'], 'w': it['w'], 'h': it['h'], 'biome': grp})
terrain_items.sort(key=lambda x:(BIOME_ORDER.index(x['biome']) if x['biome'] in BIOME_ORDER else 99, x['name']))

comp_by_biome = defaultdict(list)
for it in build_items(composite_files):
    grp, tok, feat = biome_of(it['id'])
    name = split_words(feat) or split_words(it['id'])
    comp_by_biome[grp].append({'id': it['id'], 'name': name, 'variants': it['variants'],
                               'w': it['w'], 'h': it['h']})

tiles_groups = [{'group':'Terrain', 'items': terrain_items}]
for b in BIOME_ORDER:
    if comp_by_biome.get(b):
        items = sorted(comp_by_biome[b], key=lambda x:x['name'])
        tiles_groups.append({'group': b, 'items': items})

# ===== OBJECTS =====
# props = decor + basic non-hex (petits sprites)
obj_files = [f for f in files if f['c']=='decor' or (f['c']=='basic' and not f['n'].startswith('hex'))]
obj_by_cat = defaultdict(list)
for it in build_items(obj_files):
    cat = obj_cat(it['id'])
    obj_by_cat[cat].append({'id': it['id'], 'name': split_words(it['id']), 'variants': it['variants'],
                            'w': it['w'], 'h': it['h']})
OBJ_ORDER = ['Nature','Bâtiments','Peuplements','Industrie','Agriculture','Militaire',
             'Mystère & Ruines','Voyage','Magie','Divers']
objects_groups = []
for c in OBJ_ORDER:
    if obj_by_cat.get(c):
        objects_groups.append({'group': c, 'items': sorted(obj_by_cat[c], key=lambda x:x['name'])})

# ===== ROADS / RIVERS (brut, pour plus tard) =====
roads_files = sorted([f['p'] for f in files if f['c']=='roads'])

catalog = {'tiles': tiles_groups, 'objects': objects_groups, 'roads_raw': roads_files}
with open('catalog.js','w',encoding='utf-8') as fh:
    fh.write('window.CATALOG=' + json.dumps(catalog, ensure_ascii=False) + ';')

# ---- résumé ----
print('TILES groups:')
for g in tiles_groups: print('  ', g['group'], '->', len(g['items']), 'items')
print('OBJECTS groups:')
for g in objects_groups: print('  ', g['group'], '->', len(g['items']), 'items')
print('roads/rivers raw files:', len(roads_files))
print('exemple noms roads:', [os.path.basename(x)[:-4] for x in roads_files[:12]])
print('taille catalog.js ~', round(os.path.getsize('catalog.js')/1024), 'Ko')
