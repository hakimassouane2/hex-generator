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
        ('Plains', 'hexPlains'), ('Castle', 'hexPlainsCastle'), ('Fortified Castle', 'hexPlainsCastleFortified'),
        ('Village', 'hexPlainsVillage'), ('Small Village', 'hexPlainsVillageSmall'),
        ('Thatched Village', 'hexPlainsVillageThatched'), ('Wooden Village', 'hexPlainsVillageWood'),
        ('Village Ruins', 'hexPlainsVillageRuin'), ('Farm', 'hexPlainsFarm'),
        ('Burned Farms', 'hexPlainsFarmBurned'), ('Temple', 'hexPlainsTemple'),
        ('Ruins', 'hexPlainsTempleRuins'), ('Walled City', 'hexPlainsWalledCity'),
        ('Barracks', 'hexPlainsBarracks'), ('Church', 'hexPlainsChurch'),
        ('Cookhouse', 'hexPlainsCookhouse'), ('Inn', 'hexPlainsInn'),
        ('Marketplace', 'hexPlainsMarketplace'), ('Scriptorium', 'hexPlainsScriptorium'),
        ('Smithy', 'hexPlainsSmithy'), ('Warehouse', 'hexPlainsWarehouse'),
        ('Windmill', 'hexPlainsWindmill'),
        ('Barn', 'hexPlainsFarmBarn'), ('Thatched Barn', 'hexPlainsFarmBarnThatched'), ('Wooden Barn', 'hexPlainsFarmBarnWood'),
        ('Silo', 'hexPlainsFarmSilo'), ('Thatched Silo', 'hexPlainsFarmSiloThatched'), ('Wooden Silo', 'hexPlainsFarmSiloWood'),
        ('Stronghold', 'hexPlainsStrongholdThatched'), ('Dark Wood Stronghold', 'hexPlainsStrongholdDarkWood'),
        ('Staked Stronghold', 'hexPlainsStrongholdStakes'), ('Wooden Stronghold', 'hexPlainsStrongholdWood'),
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
        ('Mountain Cave', 'hexMountainCave'), ('Mountain Castle', 'hexMountainCastle'),
        ('Mountain Fortress', 'hexMountainFortress'), ('Dwarf Fortress', 'hexMountainDwarfFortress'),
        ('Underground Gates', 'hexMountainUndergroundGateArch'),
        ('Underground Gate (Closed)', 'hexMountainUndergroundGateClosed'),
        ('Underground Gate (Natural)', 'hexMountainUndergroundGateNatural'),
        ('Underground Gate (Open)', 'hexMountainUndergroundGateOpen'),
        ('Mountains River', 'hexMountain00-river000010'), ('Highlands', 'hexHighlands'),
    ]),
    ('Hills', [
        ('Hills', 'hexHills'), ('Hills Mine', 'hexHillsMine'),
        ('Barrow Downs', 'hexHillsBarrowDowns'), ('Ruined Wizard Tower', 'hexHillsWizardTowerRuin'),
        ('Wizard Tower', 'hexHillsWizardTower'),
        ('Dark Wizard Tower', 'hexHillsWizardTowerDark'), ('Dark Wizard Tower B', 'hexHillsWizardTowerDarkB'),
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
        ('Dirt', 'hexDirt'), ('Dirt Castle', 'hexDirtCastle'), ('Dirt Castle Ruins', 'hexDirtCastleRuins'),
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

# tuiles masquées dans la palette (présentes dans les assets mais non affichées)
HIDDEN_STEMS = {'hexBase'}

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

# ============================================================================
# Taxonomie de référence des OBJETS (westmarches.games). 13 groupes ordonnés,
# transcrits du HTML du site : (nom affiché, stem du fichier). Un même stem peut
# apparaître dans plusieurs groupes (ex. loggingCamp en Industry ET Cold). Les
# stems sans asset local sont ignorés ; les objets locaux non mappés -> "Unknown".
# ============================================================================
WM_OBJ_TAXONOMY = [
    ('Nature', [
        ('Tree', 'treeA'), ('Tree B', 'treeB'), ('Tree C', 'treeC'),
        ('Tree Cluster', 'decorTreeCluster'), ('Trees Cluster', 'treesA_cluster'), ('Trees Line', 'treesA_line'),
        ('Fog', 'fog'), ('Forester Stumps', 'foresterStumps'), ('Mountain', 'decorMountain'),
        ('Pond', 'decorPond'), ('Small Lake', 'lakeSmall'),
        ('Rock Outcrop', 'outcrop'), ('Rocks', 'rocks'), ('Grass', 'grass'),
    ]),
    ('Buildings', [
        ('Forester Hut', 'foresterHut'), ('Forester Shed', 'foresterShed'),
        ('Halfling House', 'halflingHouse'), ('House', 'house'), ('Adobe House', 'houseAdobe'),
        ('Longhouse', 'houseLonghouse'), ('Round Hut', 'houseRoundHut'),
        ('Thatched House', 'houseThatched'), ('Wooden House', 'houseWood'), ('Yurt', 'houseYurt'),
        ('Barn', 'barn'), ('Wooden Barn', 'barnWood'), ('Castle', 'castle'), ('Church', 'church'),
        ('Cookhouse', 'cookhouse'), ('Dwarf Fortress', 'dwarfFortress'), ('Elven Lodge', 'elvenLodge'),
        ('Farm', 'farm'), ('Granary', 'granary'), ('Inn', 'inn'), ('Marketplace', 'marketplace'),
        ('Mountain Castle', 'mountainCastle'), ('Mountain Fortress', 'mountainFortress'),
        ('Necro Castle', 'necroCastle'), ('Scriptorium', 'scriptorium'), ('Smithy', 'smithy'),
        ('Stronghold', 'strongholdDarkWood'), ('Staked Stronghold', 'strongholdStakes'),
        ('Thatched Stronghold', 'strongholdThatched'), ('Wooden Stronghold', 'strongholdWood'),
        ('Temple', 'temple'), ('Tent', 'tent'),
        ('Warehouse', 'warehouse'), ('Windmill', 'windmill'), ('Windmill & Fields', 'windmillFields'),
        ('Wizard Tower', 'wizardTower'), ('Dark Wizard Tower', 'wizardTowerDark'), ('Dark Wizard Tower B', 'wizardTowerDark00B'),
        ('Fortified Castle', 'castleFortified'), ('Mossy Inn', 'innMossy'),
        ('Barracks', 'barracks'), ("Alchemist's Lab", 'alchemistsLab'),
        ('Archery Range', 'archeryRange'), ('Bandit Camp', 'banditCamp'), ('Barrels', 'barrels'),
    ]),
    ('Settlements', [
        ('Halfling Village', 'halflingVillage'), ('Village', 'village'), ('Small Village', 'villageSmall'),
        ('Thatched Village', 'villageThatched'), ('Wooden Village', 'villageWood'), ('Walled City', 'walledCity'),
        ('Halfling Village Decor', 'villageHalflingDecor'), ('Mossy Walled City', 'walledCityMossy'),
    ]),
    ('Industry', [
        ('Mine', 'mines'), ('Clay Pit', 'clayPit'), ('Logging Camp', 'loggingCamp'), ('Mine Entrance', 'mine'),
    ]),
    ('Agriculture', [
        ('Chicken Coop', 'chickenCoop'), ('Corral', 'corral'), ('Field', 'field'),
        ('Flock of Chickens', 'flockChickens'), ('Flock of Sheep', 'flockSheep'), ('Haystack', 'haystack'),
        ('Herd of Cows', 'herdCows'), ('Herd of Pigs', 'herdPigs'), ('Pasture', 'pasture'),
        ('Pig Pen', 'pen'), ('Pig Well', 'wellPig'),
        ('Barn', 'farmBarn'), ('Silo', 'farmSilo'), ('Stone Granary', 'granaryStone'),
        ('Thatched Granary', 'granaryThatched'), ('Wooden Granary A', 'granaryWoodA'),
        ('Wooden Granary B', 'granaryWoodB'), ('Wooden Granary C', 'granaryWoodC'),
    ]),
    ('Landmarks', [
        ('Barrow', 'barrow'), ('Fountain', 'fountain'), ('Graveyard', 'graveyard'), ('Signpost', 'sign'),
        ('Standing Stones', 'standingStones'), ('Mossy Standing Stones', 'standingStonesMossy'),
        ('Underground Passage', 'undergroundPassage'),
        ('Underground Passage (Closed)', 'undergroundPassageClosed'),
        ('Underground Passage (Open)', 'undergroundPassageOpen'),
        ('Volcano Cave', 'volcanoCave'), ('Well', 'well'),
    ]),
    ('Arcane', [
        ('Teleport Machine', 'teleportMachine'), ('Teleportation Circle', 'teleportationCircle'),
    ]),
    ('Ruins', [
        ('Castle Ruins', 'castleRuinDirt'), ('Forest Castle Ruins', 'castleRuinForest'),
        ('Marsh Castle Ruins', 'castleRuinMarsh'), ('Temple Ruins', 'templeRuins'),
        ('Village Ruins', 'villageRuin'), ('Wizard Tower Ruins', 'wizardTowerRuins'),
    ]),
    ('Water', [
        ('Bridge', 'bridgeEW'), ('Canoe', 'canou'), ('Dock', 'dockE'), ('Rocky Island', 'islandRocky'),
        ('Sandy Island', 'islandSandy'), ('Shell Building', 'shellBuilding'), ('Ship', 'ship'),
        ('Shipwreck', 'shipWreck'), ('Whirlpool', 'whirlpool'),
    ]),
    ('Cold', [
        ('Cave', 'coldLandCave'), ('Snow Cave', 'coldLandCaveSnow'), ('Frozen Giant Skeleton', 'giantSkeletonFrozen'),
        ('Iceberg', 'iceBerg'), ('Ice Crevasse', 'iceCrevasse'), ('Cold Lake', 'lakeCold'),
        ('Frozen Lake', 'lakeColdFrozen'), ('Logging Camp', 'loggingCamp'), ('Snow Logging Camp', 'loggingCampSnow'),
        ('Snow Mountain', 'mountainSnow'), ('Snow Mountain Decor', 'decorMountainSnow'),
        ('Pine Tree', 'treePine'), ('Snow Pine Tree', 'treePineSnow'),
    ]),
    ('Desert', [
        ('Obelisk', 'obelisk'), ('Desert Ruins', 'desertRuins'), ('Oasis', 'oasis'), ('Pyramid', 'pyramid'),
        ('Small Pyramid', 'pyramidSmall'), ('Sphinx', 'sphinx'), ('Cactus', 'cactus'), ('Cow Skull', 'cowSkull'),
        ('Desert Oasis', 'desertOasis'), ('Desert Tree', 'desertTree'), ('Desert Shrub', 'desertShrub'),
        ('Red Rock Formation', 'redRockBig'), ('Red Rock', 'redRock'),
        ('Yellow Rock Formation', 'yellowRockBig'),
    ]),
    ('Tropics', [
        ('Jungle Palm', 'junglePalm'), ('Jungle Tree', 'jungleTree'), ('Palm Tree', 'palm'),
        ('Stilt House', 'stiltHouse'), ('Swamp Tree', 'swampTree'),
    ]),
    ('Wastelands', [
        ('Burned Tree', 'burnedTree'), ('Hellgate', 'hellgate'), ('Lava Crater', 'lavaCraterBig'),
        ('Lava Outcrop', 'lavaOutcrop'), ('Dormant Lava Cone', 'lavaConeDormant'), ('Lava Rocks', 'lavaRocks'),
    ]),
]
WM_OBJ_GROUP_ORDER = [g for g, _ in WM_OBJ_TAXONOMY]

# objets masqués : doublons snake_case identiques aux versions camelCase déjà mappées
OBJ_HIDDEN_STEMS = {'forester_hut', 'forester_shed', 'forester_stumps', 'halfling_village'}

# stem -> [(group, name, ordre dans le groupe)]
WM_OBJ_LOOKUP = defaultdict(list)
for g, items in WM_OBJ_TAXONOMY:
    for ii, (name, stem) in enumerate(items):
        WM_OBJ_LOOKUP[stem].append((g, name, ii))

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
    if stem in HIDDEN_STEMS: continue
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
# props = decor + basic non-hex (petits sprites). Regroupés d'après WM_OBJ_TAXONOMY.
obj_files = [f for f in files if f['c']=='decor' or (f['c']=='basic' and not f['n'].startswith('hex'))]
obj_groups_map = {g: [] for g in WM_OBJ_GROUP_ORDER}
obj_groups_map['Unknown'] = []
obj_unknown_stems = []
for it in build_items(obj_files):
    stem = it['id']
    if stem in OBJ_HIDDEN_STEMS: continue
    refs = WM_OBJ_LOOKUP.get(stem)
    base = {'id': stem, 'variants': it['variants'], 'w': it['w'], 'h': it['h']}
    if refs:
        for g, name, ii in refs:
            entry = dict(base); entry['name'] = name; entry['_ord'] = ii
            obj_groups_map[g].append(entry)
    else:
        entry = dict(base); entry['name'] = split_words(stem); entry['_ord'] = 0
        obj_groups_map['Unknown'].append(entry)
        obj_unknown_stems.append(stem)

objects_groups = []
for g in WM_OBJ_GROUP_ORDER + ['Unknown']:
    lst = obj_groups_map[g]
    if not lst: continue
    lst.sort(key=lambda x: (x['_ord'], x['name']))
    for x in lst: x.pop('_ord', None)
    objects_groups.append({'group': g, 'items': lst})

# stems de la taxonomie objets sans asset correspondant (pour info)
obj_have = set(stem_of(f['n']) for f in obj_files)
obj_missing = sorted({s for s in WM_OBJ_LOOKUP if s not in obj_have})

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
print('  -> objets non reconnus (Unknown):', sorted(set(obj_unknown_stems)))
print('  -> objets de la taxonomie sans asset (', len(obj_missing), '):', obj_missing)
print('roads/rivers raw files:', len(roads_files))
print('taille catalog.js ~', round(os.path.getsize('catalog.js')/1024), 'Ko')
