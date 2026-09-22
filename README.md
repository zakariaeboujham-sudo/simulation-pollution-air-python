# Simulation numérique de la dispersion d’un polluant atmosphérique

Ce projet construit progressivement un modèle mathématique et des solveurs Python pour étudier le transport d’un polluant atmosphérique vers une zone urbaine.

Il relie analyse numérique, équations aux dérivées partielles, programmation scientifique, modélisation et environnement.

## Avancement

| Étape | Sujet | État |
|---|---|---|
| 1 | Diffusion bidimensionnelle sans vent | Code disponible |
| 2 | Transport par le vent | Code disponible |
| 3 | Source continue et zone absorbante | Code et tests disponibles |
| 4 | Capteurs, mesures bruitées et reconstruction | Code et tests disponibles |
| 5 | Reconstruction de la source | À développer |
| 6 | Optimisation environnementale | À développer |

Les quatre premières étapes disposent maintenant d'une chaîne reproductible, depuis la simulation physique jusqu'à la reconstruction d'un champ à partir de mesures bruitées. Les résultats numériques doivent être interprétés à partir des fichiers produits par une exécution locale.

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

## Étape 3 — Source continue et zone absorbante

La troisième étape ajoute une émission localisée `S` et une disparition locale `k c` :

    ∂c/∂t + u ∂c/∂x + v ∂c/∂y = D Δc + S - k c.

Le programme compare deux expériences utilisant exactement le même maillage, le même pas de temps, le même vent et la même source : une expérience sans barrière et une expérience avec ceinture absorbante. Il mesure notamment la masse absorbée et l'exposition cumulée de la zone urbaine.

Exécution complète :

~~~powershell
python src\etape_3_source_absorption.py
~~~

Exécution rapide sans GIF :

~~~powershell
python src\etape_3_source_absorption.py --taille 61 --duree 6 --sans-animation
~~~

Paramètres personnalisés :

~~~powershell
python src\etape_3_source_absorption.py --vent-x 3.5 --absorption 1.8 --duree-emission 6
~~~

## Étape 4 — Capteurs et reconstruction

La quatrième étape utilise le champ simulé comme référence, le mesure avec un réseau régulier de capteurs et ajoute un bruit gaussien reproductible. Une moyenne mobile filtre les séries temporelles, puis une interpolation par pondération inverse des distances (IDW) reconstruit le champ complet.

Le programme compare les reconstructions issues des mesures brutes et filtrées avec la référence grâce à la RMSE et à la MAE. Il exporte les positions, toutes les séries de mesure, les diagnostics et quatre figures prêtes à analyser.

Exécution complète :

~~~powershell
python src\etape_4_capteurs_reconstruction.py
~~~

Exécution rapide :

~~~powershell
python src\etape_4_capteurs_reconstruction.py --taille 61 --duree 6 --pas-mesure 0.3
~~~

Paramètres personnalisés :

~~~powershell
python src\etape_4_capteurs_reconstruction.py --capteurs-x 6 --capteurs-y 5 --bruit 12 --fenetre-filtrage 7 --graine 2026
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
    │   ├── etape_2_transport_vent.md
    │   ├── etape_3_source_absorption.md
    │   └── etape_4_capteurs_reconstruction.md
    ├── src/
    │   ├── etape_1_diffusion.py
    │   ├── etape_2_transport_vent.py
    │   ├── etape_3_source_absorption.py
    │   └── etape_4_capteurs_reconstruction.py
    └── tests/
        ├── test_etape_3.py
        └── test_etape_4.py

## Tests

Après installation des dépendances :

~~~powershell
python -m unittest discover -s tests -v
~~~

Le workflow GitHub Actions `.github/workflows/tests.yml` exécute aussi les tests sous Python 3.10, 3.11 et 3.12, puis lance une simulation rapide de l'étape 4 à chaque mise à jour de la branche `main` et pour chaque pull request.

## Résultats prévus

Le dossier resultats contiendra des cartes de concentration, des courbes de contrôle, des fichiers CSV, des bilans numériques et des animations GIF.

L'étape 3 produit notamment `comparaison_absorption.png`, `evolution_indicateurs.png`, `diagnostics.csv`, `bilan.txt` et, sauf avec l'option `--sans-animation`, `source_absorption.gif`.

L'étape 4 produit `implantation_capteurs.png`, `series_capteurs.png`, `reconstruction_champ.png`, `erreurs_reconstruction.png`, trois fichiers CSV et un bilan numérique détaillé.
