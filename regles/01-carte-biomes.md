# 01 — Carte & Biomes

## Principe
Chaque hexagone reçoit **un** des 5 biomes (abstraction du terrain dominant). Le biome indique aussi le type de monstre rencontré (voir `04-rencontres.md`). Après les biomes, on génère **un point d'intérêt par hexagone** (voir `02-points-interet.md`).

## Procédure « flocon de neige » (livre principal, p. 8-9)

### 1) Hexagone de départ (central) — 1d10
| Jet | Biome |
|----|-------|
| 1-4 | Prairie |
| 5-6 | Forêt |
| 7-8 | Collines |
| 9 | Marais |
| 10 | Montagnes |

### 2) Hexagones suivants — 1d10
| Jet | Biome |
|----|-------|
| 1-5 | **Identique à l'hexagone précédent** |
| 6 | Prairie |
| 7 | Forêt |
| 8 | Collines |
| 9 | Marais |
| 10 | Montagnes |

> La règle « 1-5 = identique » crée la continuité du terrain (lissage des biomes).

### 3) Déroulé exact
1. Générer l'hexagone **central** avec la table 1).
2. Générer les **6 hexagones autour**, en commençant par **celui du dessus** puis **dans le sens horaire**, avec la table 2). « L'hexagone précédent » = l'hexagone central. → 7 hexagones (forme de base).
3. Pour étendre : les **6 pointes** du « flocon de neige » sont générées d'abord (chacune avec comme « précédent » l'hexagone de la couche d'avant dont elle découle), puis on **complète la couche** entre les pointes. → 19 hexagones (2 couches autour du centre).
4. **Arrêt recommandé à 19 hexagones.** Pour une carte plus grande : répéter la procédure et **coller plusieurs cartes** ensemble (méthode utilisée dans le reste du livre).

> Pour le générateur, « l'hexagone précédent » d'un nouvel hexagone = un voisin déjà généré appartenant à la couche intérieure (plus proche du centre). C'est ce voisin qui sert de base à la règle « 1-5 = identique ».

## Numérotation
Système de numérotation par hexagone (1, 2, 3…). Pour coller plusieurs cartes, garder la même numérotation par carte mais préfixer d'une **lettre majuscule** (carte A, B, …).

## Légende des symboles de biome
Prairie · Forêt · Collines · Marais · Montagnes (symboles dans le PDF ; pour le MVP on utilise une couleur par biome).

---

# Extension Biomes — Climats & biomes profonds

## Climats
3 climats selon la température moyenne (la précipitation n'est pas prise en compte) : **Tempéré, Chaud, Froid**. Chaque biome tempéré a un équivalent dans les autres climats (même rang de difficulté).

### Équivalence des biomes par climat
| Tempéré | Froid | Chaud |
|---------|-------|-------|
| Prairie (Grassland) | Lande (Moor) | Savane (Savanna) |
| Forêt de feuillus (Deciduous forest) | Forêt de conifères (Evergreen forest) | Forêt tropicale (Tropical forest) |
| Collines (Hills) | Toundra (Tundra) | Désert (Desert) |
| Marais (Marsh) | Champs de neige (Snowfields) | Marécage (Swamp) |
| Montagnes (Mountains) | Pics gelés (Frozen peaks) | Plateau (Plateau) |

Les tables de biome (départ / suivant, 1d10) s'utilisent à l'identique, en lisant la colonne du climat voulu. On peut générer en tempéré puis **traduire** via ce tableau.

### Méthode 1 — bandes de latitude
Tracer 2 lignes horizontales sur la carte du monde : entre elles = tempéré, au-dessus = froid, en-dessous = chaud. Affecter le climat à des cartes entières ou à des hexagones individuels (le côté de plus grande aire l'emporte). Distribution plus crédible.

### Méthode 2 — flocon de neige par CARTE
Appliquer la méthode flocon mais à l'échelle des **cartes** (chaque carte = un climat).
- Climat de la carte de départ : 1d10 → **1-5 Tempéré, 6-8 Froid, 9-10 Chaud** (ou au choix).
- Cartes suivantes (1d10), selon le climat de la carte de départ :
  - **Tempéré** : 1-6 Identique · 7-8 Froid · 9-10 Chaud
  - **Froid** : 1-6 Identique · 7-9 Tempéré · 10 Chaud
  - **Chaud** : 1-6 Identique · 7-9 Tempéré · 10 Froid
- Puis biome de chaque hexagone via les tables p. 4.

### Méthode 3 — flocon par HEXAGONE
Idem méthode 2 mais le climat est tiré par hexagone (plus long, situations à interpréter). Tirer d'abord le climat de chaque hex, puis le biome.

## Biomes profonds (« deep biomes »)
Variations **rares** d'un biome normal. Apparaissent quand un **amas de 7 hexagones du même biome** est généré : le biome de l'hexagone **central** est alors remplacé par le biome profond. Probabilité < 5 % (hors collage de cartes). Zones très spéciales, plus dangereuses, avec leur propre petite table de rencontres (1d6).

| Climat | Biome normal | Biome profond | Description | Rencontres (1d6) |
|--------|--------------|---------------|-------------|------------------|
| Tempéré | Prairie | Champ de trèfle (Clover field) | Prairie de trèfles | 1-3 Leprechauns · 4-5 Limaces géantes · 6 Licornes |
| Tempéré | Forêt feuillus | Forêt hantée (Haunted forest) | Bois sinistre habité d'esprits | 1-3 Loups-garous · 4-5 Fantômes · 6 Arbres tueurs |
| Tempéré | Collines | Vallée inondée (Flooded valley) | Inondation/rupture de barrage | 1-3 Anguilles · 4-5 Hommes-poissons · 6 Castors géants |
| Tempéré | Marais | Forêt fongique (Fungal forest) | Champignons de la taille d'arbres | 1-3 Hurleurs · 4-5 Hommes-champignons · 6 Fongoïdes |
| Tempéré | Montagnes | Volcan (Volcano) | Lave, roches, cendres | 1-3 Salamandres de feu · 4-5 Efreets · 6 Phénix |
| Froid | Lande | Marais tourbeux (Fen) | Zone marécageuse/tourbeuse | 1-3 Momies des tourbières · 4-5 Mégères vertes · 6 Fantômes |
| Froid | Forêt conifères | Forêt maudite (Cursed forest) | Zone corrompue, arbres morts | 1-3 Squelettes · 4-5 Cauchemars · 6 Spectres (Wights) |
| Froid | Toundra | Sources chaudes (Hot springs) | Bassins d'eau chaude naturels | 1-3 Ours · 4-5 Méphites de vapeur · 6 Néréides |
| Froid | Champs de neige | Glacier (Glacier) | Glace pérenne avançant lentement | 1-3 Yétis · 4-5 Géants du givre · 6 Remorhaz |
| Froid | Pics gelés | Sols cristallins (Crystal grounds) | Roche où poussent des cristaux | 1-3 Salamandres de givre · 4-5 Élémentaires de pierre · 6 Crysmals |
| Chaud | Savane | Champ d'épines (Thorn field) | Végétation épineuse dense | 1-3 Lianes constrictrices · 4-5 Plantes-pièges · 6 Vegepygmées |
| Chaud | Forêt tropicale | Jungle primale (Primal jungle) | Étendue sauvage inexplorée | 1-3 Singes carnivores · 4-5 Serpents géants · 6 Hydres |
| Chaud | Désert | Oasis (Oasis) | Point d'eau où la vie prospère | 1-3 Hippopotames · 4-5 Nomades · 6 Manticores |
| Chaud | Marécage | Marécage toxique (Toxic swamp) | Lieu où tout est empoisonné | 1-3 Cobras cracheurs · 4-5 Libellules géantes · 6 Basilics |
| Chaud | Plateau | Vallée perdue (Lost valley) | Évolution figée à la préhistoire | 1-3 Néandertaliens · 4-5 Dinosaures · 6 Mastodontes |

### Particularités de biomes profonds
- Forêt hantée / maudite : pénalité de moral aux suivants **-1** / **-2**.
- Forêt fongique : par jour passé, JdS contre poison ou maladie (moisissure rampante, boules de spores, éruptions « redcap »).
- Oasis : 25 % de chance d'être une **illusion**.
