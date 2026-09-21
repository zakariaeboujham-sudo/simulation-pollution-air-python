# Simulation numérique de la dispersion d’un polluant atmosphérique

Ce projet construit progressivement un modèle mathématique et des solveurs Python pour étudier le transport d’un polluant atmosphérique vers une zone urbaine.

Il relie analyse numérique, équations aux dérivées partielles, programmation scientifique, modélisation et environnement.

## Avancement

| Étape | Sujet | État |
|---|---|---|
| 1 | Diffusion bidimensionnelle sans vent | Code disponible |
| 2 | Transport par le vent | Code disponible |
| 3 | Source continue et zone absorbante | À développer |
| 4 | Capteurs et mesures bruitées | À développer |
| 5 | Reconstruction de la source | À développer |
| 6 | Optimisation environnementale | À développer |

Les codes des étapes 1 et 2 doivent encore être exécutés dans un environnement Python avant de publier des résultats numériques comme résultats obtenus.

## Étape 1 — Diffusion sans vent

La première étape résout

    ∂c/∂t = D Δc.

Une tache gaussienne représente le polluant initial. Un schéma d’Euler explicite et un laplacien à cinq points simulent son étalement. Le programme contrôle la stabilité, la positivité et la conservation de la masse.

Exécution :

~~~powershell
python src\etape_1_diffusion.py
~~~

## Étape 2 — Transport par le vent

La deuxième étape résout

    ∂c/∂t + u ∂c/∂x + v ∂c/∂y = D Δc.

Le terme d’advection représente le déplacement causé par le vent. Il est discrétisé par un schéma amont. Trois scénarios sont comparés : sans vent, vent horizontal et vent oblique.

Le programme suit aussi le centre de masse du nuage de pollution afin de mesurer son déplacement.

Exécution :

~~~powershell
python src\etape_2_transport_vent.py
~~~

Paramètres personnalisés :

~~~powershell
python src\etape_2_transport_vent.py --vent-x 3 --vent-y 0.8 --duree 10
~~~

## Installation

Python 3.10 ou une version plus récente est recommandé.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

## Structure

    simulation-pollution-air/
    ├── README.md
    ├── requirements.txt
    ├── docs/
    │   ├── plan_scientifique.md
    │   └── etape_2_transport_vent.md
    └── src/
        ├── etape_1_diffusion.py
        └── etape_2_transport_vent.py

## Résultats prévus

Le dossier resultats contiendra des cartes de concentration, des courbes de contrôle, des fichiers CSV, des bilans numériques et des animations GIF.

Les figures réellement obtenues seront ajoutées après exécution et contrôle des résultats.
