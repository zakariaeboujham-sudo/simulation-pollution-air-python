# Étape 4 — Capteurs, mesures bruitées et reconstruction

## Objectif

Cette étape transforme le champ simulé en une expérience de mesure réaliste et reproductible. Un réseau de capteurs échantillonne le panache, les mesures sont perturbées par un bruit instrumental, puis filtrées avant de reconstruire une carte complète de concentration.

## Chaîne de traitement

1. Le solveur d'advection-diffusion-réaction de l'étape 3 calcule un champ de référence avec source et ceinture absorbante.
2. Les capteurs sont répartis sur une grille régulière à l'intérieur du domaine et placés exactement sur des nœuds du maillage.
3. Le champ est échantillonné à un intervalle réglable avec `--pas-mesure`.
4. Un bruit gaussien d'écart-type réglable est ajouté. La graine aléatoire fixe rend l'expérience reproductible.
5. Une moyenne mobile centrée réduit les fluctuations rapides.
6. Une interpolation par pondération inverse des distances, ou IDW, reconstruit le champ sur tout le maillage.
7. Les reconstructions issues des mesures brutes et filtrées sont comparées au champ de référence avec la RMSE et la MAE.

Le niveau passé avec `--bruit` représente un pourcentage de la plus grande concentration exacte observée par le réseau. Les valeurs bruitées négatives sont ramenées à zéro, conformément à la positivité physique de la concentration.

## Modèle de reconstruction

Pour une position `r`, l'estimation IDW s'écrit

    c_est(r) = somme_i w_i(r) c_i / somme_i w_i(r),
    w_i(r) = 1 / distance(r, r_i)^p.

La puissance `p`, égale à 2 par défaut, règle le caractère local de l'interpolation. La valeur mesurée est reproduite exactement sur chaque capteur.

L'IDW exploite uniquement la géométrie du réseau. Il ne connaît ni le vent, ni la diffusion, ni la source. Il fournit donc une première reconstruction pédagogique, mais pas encore une assimilation optimale du modèle physique.

## Exécution

Simulation par défaut :

~~~powershell
python src\etape_4_capteurs_reconstruction.py
~~~

Calcul rapide :

~~~powershell
python src\etape_4_capteurs_reconstruction.py --taille 61 --duree 6 --pas-mesure 0.3
~~~

Expérience personnalisée :

~~~powershell
python src\etape_4_capteurs_reconstruction.py --capteurs-x 6 --capteurs-y 5 --bruit 12 --fenetre-filtrage 7 --graine 2026
~~~

## Fichiers produits

- `implantation_capteurs.png` : position et identifiant de tous les capteurs ;
- `series_capteurs.png` : référence, mesure bruitée et mesure filtrée pour quatre capteurs représentatifs ;
- `reconstruction_champ.png` : champ final exact, reconstructions brute et filtrée, puis erreur absolue ;
- `erreurs_reconstruction.png` : évolution de la RMSE et de la MAE ;
- `positions_capteurs.csv` : coordonnées et indices de maillage ;
- `mesures_capteurs.csv` : séries temporelles complètes ;
- `diagnostics_reconstruction.csv` : erreurs spatiales à chaque instant mesuré ;
- `bilan.txt` : paramètres et synthèse quantitative.

## Interprétation

Le filtrage réduit en principe la variance instrumentale, mais une fenêtre trop large lisse aussi les variations rapides du panache. De même, augmenter le nombre de capteurs améliore généralement l'interpolation sans supprimer le biais d'une méthode purement géométrique. Ces compromis préparent l'étape 5, où la position et l'intensité de la source seront estimées par un problème inverse fondé sur le modèle physique.
