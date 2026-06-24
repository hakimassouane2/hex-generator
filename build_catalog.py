# Génère catalog.js (catalogue structuré pour l'éditeur) à partir des PNG.
# Les TUILES (full-hex 256x384) sont regroupées d'après la taxonomie du site de
# référence (westmarches.games) : groupe "Terrain" (sélection rapide) puis groupes
# par biome. Toute tuile présente dans nos assets mais absente de la taxonomie est
# rangée dans "Unknown" (à trier manuellement plus tard).
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

def split_words(s):
    s = re.sub(r'(\d+)(_[a-zA-Z]+)?$', '', s)
    s = s.replace('_', ' ')
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    return s.strip().title()

# ============================================================================
# Taxonomie de référence (westmarches.games). Chaque groupe : liste ordonnée de
# (nom affiché, stem du fichier). Un même stem peut apparaître dans plusieurs
# groupes (ex. "Terrain" duplique des tuiles ; les pins sont en Forest ET Cold).
# ============================================================================
WM_TAXONOMY = [
    ('Terrain', [
        ('Plains', 'hexPlains'), ('Forest', 'hexForestBroadleaf'),
        ('Mountains', 'hexMountain'), ('Mountains River', 'hexMountain00-river000010'),
        ('Hills', 'hexHills'), ('Desert', 'hexDesertDunes'),
        ('Lake', 'hexLake'), ('Calm Ocean', 'hexOceanCalm'), ('Ocean', 'hexOcean'),
        ('Marsh', 'hexMarsh'), ('Dirt', 'hexDirt'), ('Highlands', 'hexHighlands'),
        ('Scrublands', 'hexScrublands'), ('Woodlands', 'hexWoodlands'),
    ]),
    ('Plains', [
        ('Plains', 'hexPlains'), ('Castle', 'hexPlainsCastle'),
        ('Village', 'hexPlainsVillage'), ('Small Village', 'hexPlainsVillageSmall'),
        ('Thatched Village', 'hexPlainsVillageThatched'), ('Wooden Village', 'hexPlainsVillageWood'),
        ('Village Ruins', 'hexPlainsVillageRuin'), ('Farm', 'hexPlainsFarm'),
        ('Burned Farms', 'hexPlainsFarmBurned'), ('Temple', 'hexPlainsTemple'),
        ('Ruins', 'hexPlainsTempleRuins'), ('Walled City', 'hexPlainsWalledCity'),
        ('Barracks', 'hexPlainsBarracks'), ('Church', 'hexPlainsChurch'),
        ('Cookhouse', 'hexPlainsCookhouse'), ('Inn', 'hexPlainsInn'),
        ('Marketplace', 'hexPlainsMarketplace'), ('Scriptorium', 'hexPlainsScriptorium'),
        ('Smithy', 'hexPlainsSmithy'), ('Warehouse', 'hexPlainsWarehouse'),
        ('Windmill', 'hexPlainsWindmill'), ('Barn', 'hexPlainsFarmBarn'),
        ('Silo', 'hexPlainsFarmSilo'), ('Stronghold', 'hexPlainsStrongholdThatched'),
        ('Halfling Village', 'hexPlainsHalflingVillage'), ('Elven Lodge', 'hexPlainsElvenLodge'),
        ('Henge', 'hexPlainsHenge'),
    ]),
    ('Forest', [
        ('Forest', 'hexForestBroadleaf'), ('Bandit Camp', 'hexForestBroadleafBanditCamp'),
        ('Forest Clearing', 'hexForestBroadleafClearing'), ('Elf Village', 'hexForestBroadleafElfVillage'),
        ('Elf Ruins', 'hexForestBroadleafElfRuins'), ('Forester Hut', 'hexForestBroadleafForester'),
        ('Giant Tree', 'hexForestBroadleafGiantTree'), ('Standing Stones', 'hexForestBroadleafStandingStones'),
        ('Elven Lodge', 'hexForestElvenLodge'), ('Forest Ruins', 'hexForestCastleRuins'),
        ('Pine Forest', 'hexForestPine'), ('Pine Forest Clearing', 'hexForestPineClearing'),
        ('Pine Forest Logging Camp', 'hexForestPineLoggingCamp'),
    ]),
    ('Mountain', [
        ('Mountains', 'hexMountain'), ('Mountain Mine', 'hexMountainMine'),
        ('Mountain Cave', 'hexMountainCave'), ('Mountain Fortress', 'hexMountainFortress'),
        ('Dwarf Fortress', 'hexMountainDwarfFortress'), ('Underground Gates', 'hexMountainUndergroundGateArch'),
        ('Mountains River', 'hexMountain00-river000010'), ('Highlands', 'hexHighlands'),
    ]),
    ('Hills', [
        ('Hills', 'hexHills'), ('Hills Mine', 'hexHillsMine'),
        ('Barrow Downs', 'hexHillsBarrowDowns'), ('Ruined Wizard Tower', 'hexHillsWizardTowerRuin'),
        ('Wizard Tower', 'hexHillsWizardTower'),
    ]),
    ('Desert', [
        ('Desert', 'hexDesertDunes'), ('Desert Oasis', 'hexDesertDunesOasis'),
        ('Desert Pyramids', 'hexDesertDunesPyramids'), ('Desert Sphinx', 'hexDesertDunesSphinx'),
        ('Desert Ruins', 'hexDesertDunesRuins'),
        ('Red Desert Base', 'hexDesertRedBase'), ('Red Desert Dirt', 'hexDesertRedDirt'),
        ('Red Desert Forest', 'hexDesertRedForest'), ('Red Desert Forest Oasis', 'hexDesertRedForestOasis'),
        ('Red Desert Grass', 'hexDesertRedGrass'), ('Red Desert Grass Dunes', 'hexDesertRedGrassDunes'),
        ('Red Desert Grass Oasis', 'hexDesertRedGrassOasis'), ('Red Desert Hills', 'hexDesertRedHills'),
        ('Red Desert Hills Oasis', 'hexDesertRedHillsOasis'), ('Red Desert Large Mesa', 'hexDesertRedMesaLarge'),
        ('Red Desert Large Mesa Cave', 'hexDesertRedMesaLargeCave'), ('Red Desert Mountains', 'hexDesertRedMountains'),
        ('Red Desert Mountains Cave', 'hexDesertRedMountainsCave'),
        ('Yellow Desert Base', 'hexDesertYellowBase'), ('Yellow Desert Cacti Forest', 'hexDesertYellowCactiForest'),
        ('Yellow Desert Crater', 'hexDesertYellowCrater'), ('Yellow Desert Dirt', 'hexDesertYellowDirt'),
        ('Yellow Desert Dirt Dunes', 'hexDesertYellowDirtDunes'), ('Yellow Desert Hills', 'hexDesertYellowHills'),
        ('Yellow Desert Hills Oasis', 'hexDesertYellowHillsOasis'), ('Yellow Desert Large Mesa', 'hexDesertYellowMesaLarge'),
        ('Yellow Desert Large Mesa Cave', 'hexDesertYellowMesaLargeCave'), ('Yellow Desert Large Mesa Oasis', 'hexDesertYellowMesaLargeOasis'),
        ('Yellow Desert Mesas', 'hexDesertYellowMesas'), ('Yellow Desert Mesas Cave', 'hexDesertYellowMesasCave'),
        ('Yellow Desert Salt Flat', 'hexDesertYellowSaltFlat'),
    ]),
    ('Water', [
        ('Lake', 'hexLake'), ('Calm Ocean', 'hexOceanCalm'), ('Ocean', 'hexOcean'),
        ('Rocky Island', 'hexIslandRocky'), ('Sandy Island', 'hexIslandSandy'),
        ('Whirlpool', 'hexOceanWhirlpool'), ('Shipwreck', 'hexOceanShipWreck'),
        ('Whaling Harbor', 'hexOceanHarborWhaling'), ('Shell Village', 'hexOceanShellVillage'),
        ('Rocky Island Tower', 'hexIslandRockyTower'), ('Rocky Island House', 'hexIslandRockyHouse'),
        ('Sandy Island Shipwreck', 'hexIslandSandyShipWreck'), ('Sandy Island Temple', 'hexIslandSandyTemple'),
        ('Ice Berg Ocean', 'hexOceanIceBergs'),
    ]),
    ('Cold', [
        ('Cold Dirt', 'hexDirtCold'),
        ('Pine Forest', 'hexForestPine'), ('Pine Forest Clearing', 'hexForestPineClearing'),
        ('Pine Forest Logging Camp', 'hexForestPineLoggingCamp'),
        ('Snow-Covered Pine Forest', 'hexForestPineSnowCovered'), ('Snow-Covered Pine Forest Clearing', 'hexForestPineSnowCoveredClearing'),
        ('Snow-Covered Pine Forest Logging Camp', 'hexForestPineSnowCoveredLoggingCamp'),
        ('Pine Forest Snow Transition', 'hexForestPineSnowTransition'), ('Pine Forest Snow Transition Clearing', 'hexForestPineSnowTransitionClearing'),
        ('Pine Forest Snow Transition Logging Camp', 'hexForestPineSnowTransitionLoggingCamp'),
        ('Cold Hills', 'hexHillsCold'), ('Cold Hills Cave', 'hexHillsColdCave'),
        ('Snow-Covered Cold Hills', 'hexHillsColdSnowCovered'), ('Snow-Covered Cold Hills Cave', 'hexHillsColdSnowCoveredCave'),
        ('Cold Hills Snow Transition', 'hexHillsColdSnowTransition'), ('Cold Hills Snow Transition Cave', 'hexHillsColdSnowTransitionCave'),
        ('Snow Mountain', 'hexMountainSnow'), ('Snow Mountain Cave', 'hexMountainSnowCave'),
        ('Ice Berg Ocean', 'hexOceanIceBergs'),
        ('Cold Plains', 'hexPlainsCold'), ('Cold Plains Pond', 'hexPlainsColdPond'),
        ('Cold Plains Ruin', 'hexPlainsColdRuin'), ('Cold Plains Ruin Snow', 'hexPlainsColdRuinSnow'),
        ('Snow-Covered Cold Plains', 'hexPlainsColdSnowCovered'), ('Snow-Covered Cold Plains Pond', 'hexPlainsColdSnowCoveredPond'),
        ('Cold Plains Snow Transition', 'hexPlainsColdSnowTransition'), ('Cold Plains Snow Transition Pond', 'hexPlainsColdSnowTransitionPond'),
        ('Snow Field', 'hexSnowField'), ('Snow Field Giant Skeleton', 'hexSnowFieldGiantSkeleton'),
        ('Snow Field Ice Palace', 'hexSnowFieldIcePalace'),
    ]),
    ('Marsh', [
        ('Marsh', 'hexMarsh'), ('Marsh Graveyard', 'hexMarshGraveyard'),
        ('Marsh Stilt Village', 'hexMarshStiltVillage'), ('Marsh Snake Temple', 'hexMarshSnakeTemple'),
        ('Marsh Ruins', 'hexMarshCastleRuins'),
    ]),
    ('Dirt', [
        ('Dirt', 'hexDirt'), ('Dirt Castle', 'hexDirtCastle'),
        ('Dirt Village', 'hexDirtVillage'), ('Dirt Small Village', 'hexDirtVillageSmall'),
        ('Dirt Village Ruins', 'hexDirtVillageRuin'), ('Dirt Temple', 'hexDirtTemple'),
        ('Dirt Ruins', 'hexDirtTempleRuins'), ('Dirt Inn', 'hexDirtInn'),
        ('Dirt Smithy', 'hexDirtSmithy'), ('Dirt Walled City', 'hexDirtWalledCity'),
        ('Dirt Henge', 'hexDirtHenge'), ('Dirt Clay Pit', 'hexDirtClayPit'),
    ]),
    ('Tropics', [
        ('Bog', 'hexBog'), ('Grassy Sand', 'hexGrassySand'),
        ('Grassy Sand Palms', 'hexGrassySandPalms'), ('Jungle', 'hexJungle'),
        ('Tropical Sand', 'hexSand'), ('Tropical Sand Palms', 'hexSandPalms'),
        ('Tropical Swamp', 'hexSwamp'), ('Tropical Plains', 'hexTropicalPlains'),
        ('Tropical Plains Ruin Machine', 'hexTropicalPlainsRuinMachine'),
        ('Tropical Plains Snake Temple', 'hexTropicalPlainsSnakeTemple'),
        ('Tropical Plains Stepped Pyramid', 'hexTropicalPlainsSteppedPyramid'),
        ('Tropical Plains Stepped Pyramid Ruin', 'hexTropicalPlainsSteppedPyramidRuin'),
        ('Tropical Waterfall Hill', 'hexTropicalWaterfallHill'), ('Wetlands', 'hexWetlands'),
        ('Wetlands Snake Temple', 'hexWetlandsSnakeTemple'), ('Wetlands Stilt Village', 'hexWetlandsStiltVillage'),
    ]),
    ('Wasteland', [
        ('Ash Plains', 'hexAshPlains'), ('Burned Forest Ash', 'hexForestBurnedAsh'),
        ('Burned Forest Dirt', 'hexForestBurnedDirt'), ('Fumarole Plains', 'hexFumarolePlains'),
        ('Lava Field', 'hexLavaField'), ('Active Lava Field', 'hexLavaFieldActive'),
        ('Lava Sea', 'hexLavaSea'), ('Active Volcano', 'hexVolcanoActive'),
        ('Dormant Volcano', 'hexVolcanoDormant'), ('Volcano Cave', 'hexVolcanoCave'),
        ('Necromancer Castle', 'hexForestBurnedAshNecroCastle'),
    ]),
    ('Void', [
        ('Void', 'hexVoid'),
    ]),
]
WM_GROUP_ORDER = [g for g, _ in WM_TAXONOMY]

# stem -> [(group, name, ordre dans le groupe)]
WM_LOOKUP = defaultdict(list)
for g, items in WM_TAXONOMY:
    for ii, (name, stem) in enumerate(items):
        WM_LOOKUP[stem].append((g, name, ii))

# socle 2.5D à dessiner sous la tuile : eau -> océan, vide -> aucun, reste -> terre
def under_of(stem):
    if re.search(r'Ocean|Lake|Island', stem): return 'ocean'
    if stem.startswith('hexVoid'): return 'none'
    return 'dirt'

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

# ---- regrouper en items (variantes) par stem ----
def build_items(file_list):
    groups = defaultdict(list)
    for f in file_list:
        groups[stem_of(f['n'])].append(f)
    items = []
    for stem, fs in groups.items():
        fs.sort(key=lambda x: x['n'])
        w, h = fs[0]['w'], fs[0]['h']
        items.append({'id': stem, 'variants': [f['p'] for f in fs], 'w': w, 'h': h})
    return items

# ===== TILES =====
# Une tuile = full-hex 256x384 (terrains de base, "Base Tiles" et tuiles composites
# "Tiles/"). Les petits sprites/decor restent dans les OBJETS.
tile_files = [f for f in files if f['w'] == 256 and f['h'] == 384 and f['c'] in ('basic', 'base', 'composite')]

groups_map = {g: [] for g in WM_GROUP_ORDER}
groups_map['Unknown'] = []
unknown_stems = []
for it in build_items(tile_files):
    stem = it['id']
    refs = WM_LOOKUP.get(stem)
    under = under_of(stem)
    base = {'id': stem, 'variants': it['variants'], 'w': it['w'], 'h': it['h'], 'under': under}
    if refs:
        for g, name, ii in refs:
            entry = dict(base); entry['name'] = name; entry['_ord'] = ii
            groups_map[g].append(entry)
    else:
        entry = dict(base)
        entry['name'] = split_words(stem[3:] if stem.startswith('hex') else stem)
        entry['_ord'] = 0
        groups_map['Unknown'].append(entry)
        unknown_stems.append(stem)

tiles_groups = []
for g in WM_GROUP_ORDER + ['Unknown']:
    lst = groups_map[g]
    if not lst: continue
    lst.sort(key=lambda x: (x['_ord'], x['name']))
    for x in lst: x.pop('_ord', None)
    tiles_groups.append({'group': g, 'items': lst})

# stems de la taxonomie sans asset correspondant (pour info)
have = set(stem_of(f['n']) for f in tile_files)
missing = sorted({s for s in WM_LOOKUP if s not in have})

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
print('  -> tuiles non reconnues (Unknown):', sorted(set(unknown_stems)))
print('  -> tuiles de la taxonomie sans asset (', len(missing), '):', missing)
print('OBJECTS groups:')
for g in objects_groups: print('  ', g['group'], '->', len(g['items']), 'items')
print('roads/rivers raw files:', len(roads_files))
print('taille catalog.js ~', round(os.path.getsize('catalog.js')/1024), 'Ko')
