# Simulation numérique de la dispersion d’un polluant atmosphérique

Ce projet construit progressivement un modèle mathématique et un solveur Python pour étudier le transport d’un polluant atmosphérique vers une zone urbaine.

Le projet complet ajoutera successivement :

1. la diffusion du polluant sans vent ;
2. le transport par le vent ;
3. une zone absorbante représentant une ceinture végétale ;
4. des capteurs fournissant des mesures bruitées ;
5. la reconstruction de la source de pollution ;
6. l’optimisation de la position de la ceinture végétale.

## Étape 1 — Diffusion bidimensionnelle sans vent

La première étape résout l’équation

    ∂c/∂t = D Δc

sur un domaine carré. La concentration initiale est une tache gaussienne localisée. Les frontières sont imperméables : aucun polluant ne quitte le domaine.

Cette étape sert à vérifier :

- la stabilité du schéma numérique ;
- la positivité de la concentration ;
- la conservation de la masse totale ;
- la symétrie de la diffusion ;
- la reproductibilité des résultats.

## Méthode numérique

L’espace est discrétisé par différences finies avec un laplacien à cinq points. Le temps est avancé par un schéma d’Euler explicite. Le pas de temps est choisi automatiquement pour respecter la condition de stabilité

    Δt ≤ Δx² / (4D).

## Installation

Python 3.10 ou une version plus récente est recommandé.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

## Exécution

~~~powershell
python src\etape_1_diffusion.py
~~~

Paramètres personnalisés :

~~~powershell
python src\etape_1_diffusion.py --taille 121 --duree 12 --diffusion 5 --sortie resultats
~~~

## Résultats produits

Le dossier resultats contiendra :

- diffusion_instants.png : cartes de concentration à plusieurs instants ;
- conservation_masse.png : évolution de la masse totale ;
- diffusion.gif : animation temporelle ;
- bilan.txt : paramètres et indicateurs numériques ;
- conservation_masse.csv : valeurs utilisées pour le contrôle.

## Structure destinée à GitHub

    simulation-pollution-air/
    ├── README.md
    ├── requirements.txt
    ├── docs/
    │   └── plan_scientifique.md
    └── src/
        └── etape_1_diffusion.py

Les figures réellement obtenues seront ajoutées après exécution et contrôle des résultats.
