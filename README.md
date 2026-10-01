# Simulation numérique de la pollution atmosphérique

Ce projet pédagogique étudie le transport d'un polluant vers une ville et la
réduction de son exposition par une ceinture absorbante. Il relie un modèle
physique, des mesures simulées, une estimation de source et une comparaison
coût/efficacité. Les six étapes sont présentes dans ce dépôt.

## Installation et lancement

Python 3.10 ou plus récent :

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python lancer.py
~~~

Le lanceur exécute les étapes 3 à 6 et produit les figures, CSV et bilans dans
resultats/. Aucun service, compte ou jeu de données externe n'est nécessaire.

## Étapes

1. **Diffusion** : étalement d'une concentration initiale, sans vent.
2. **Vent** : advection amont et déplacement du nuage.
3. **Source et absorption** : comparaison avec/sans ceinture, bilan de masse et exposition urbaine cumulée.
4. **Capteurs** : réseau régulier, bruit reproductible, filtre temporel et reconstruction IDW ; comparaison RMSE/MAE.
5. **Problème inverse** : recherche parmi 20 positions et estimation de l'intensité par moindres carrés.
6. **Optimisation** : comparaison de 18 ceintures, score combinant exposition et coût conventionnel.

Chaque étape peut être exécutée seule :

~~~powershell
python src/etape_1_diffusion.py
python src/etape_2_transport_vent.py
python src/etape_3_source_absorption.py --taille 41 --sans-animation
python src/etape_4_capteurs_reconstruction.py --taille 41 --duree 24
python src/etape_5_probleme_inverse.py
python src/etape_6_optimisation.py
python -m unittest discover -s tests -v
~~~

Utiliser --help pour les options de chaque script. Les étapes 4 à 6 utilisent
un domaine de 100 km, le vent (3 ; 0,3) km/h et la diffusion 1,5 km²/h. Leur
configuration simple est détaillée dans [docs/completion.md](docs/completion.md).
Les étapes 1 à 3 conservent leurs paramètres propres.

## Résultats et interprétation

- Étape 3 : evolution_avec_ceinture.png, comparaison_finale.png,
  exposition_urbaine.png, bilan_masse.png, diagnostics.csv, bilan.txt ;
  source_et_ceinture.gif si l'animation est activée.
- Étape 4 : quatre figures, positions et séries des capteurs, diagnostics CSV,
  bilan.json avec les paramètres et erreurs finales.
- Étape 5 : candidats.csv et bilan.json avec source vraie et estimée.
- Étape 6 : comparaison_ceintures.csv, cout_efficacite.png, bilan.json.

Les sorties sont régénérées localement par les scripts. Le compte rendu
et les résultats chiffrés se trouvent dans [docs/verification.md](docs/verification.md).
Ils concernent uniquement une expérience synthétique. Les frontières sont
fermées, le vent constant et l'absorption simplifiée. Le coût n'est pas un prix
économique réel. La recherche est discrète et ne garantit pas un optimum global.
Une étude de convergence systématique et une validation avec des mesures réelles
restent nécessaires avant toute application environnementale.

## Vérification automatique

Les tests contrôlent conservation des flux, bilan de masse, positivité,
réduction de l'exposition, propriétés de l'IDW, filtrage et estimation linéaire.
Le workflow .github/workflows/tests.yml les exécute sous Python 3.10, 3.11
et 3.12 à chaque push et pull request.
