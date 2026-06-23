# Cerveau — Sandbox Generator (Atelier Clandestin)

Ce dossier est la **base de règles de référence** extraite des PDF (livre principal `sandbox-generator-fr.pdf` + extensions Biomes, Factions, Landmarks). Objectif : que le générateur et l'assistant s'appuient sur des règles **exactes**, sans halluciner.

> Portée actuelle = **génération de la carte** (biomes, points d'intérêt, peuplements, points de repère, factions, rencontres, noms). Les sections « contenu détaillé » du livre (donjons, salles, peuplements détaillés, générateurs de blason/dragon/guilde/PNJ, mer) ne sont **pas** encore transcrites ici.

## Fichiers
- `01-carte-biomes.md` — Procédure de génération de la carte (méthode « flocon de neige »), tables de biomes, climats et biomes profonds (extension Biomes).
- `02-points-interet.md` — Tables de points d'intérêt et de peuplements.
- `03-points-de-repere.md` — Points de repère naturels / artificiels / magiques + table « Contenu » (Danger / Vide / Spécial / Monstres) + trésor.
- `04-rencontres.md` — Rencontres par biome (tempéré + climats chaud/froid) + table de rencontres aléatoires.
- `05-factions.md` — Carte politique, territoires, titres de noblesse, relations, événements, noms de factions, générateur de noble.
- `06-noms.md` — Générateur de noms de peuplements (hameaux/villages/villes).

## Concept général du livre
Génération **du général vers le particulier** : on part d'une carte de biomes + points d'intérêt, puis on détaille progressivement (points de repère, peuplements, repaires, donjons), puis on étoffe avec des générateurs ciblés.

- Échelle de référence : **hexagones de 2 miles (≈ 3,33 km)**.
- Dés nécessaires : jeu complet (d4, d6, d8, d10, d12, d20, d100) **+ d24 + d30**.
  - **d24** émulé par 1d2 + 1d12 : sur un 2 au d2, ajouter 12 au d12.
  - **d30** émulé par 1d3 + 1d10 : sur un 2 au d3 ajouter 10, sur un 3 ajouter 20.
- **Jet de pourcentage (d100)** : réussite si le jet est **≤** au pourcentage cible.
- Tout résultat aléatoire peut être ignoré, modifié ou relancé : le livre est un guide, pas une loi.

## 5 biomes de base (climat tempéré)
Prairie · Forêt · Collines · Marais · Montagnes — du plus facile au plus difficile à traverser.
