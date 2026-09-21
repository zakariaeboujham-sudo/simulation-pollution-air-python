# Plan scientifique du projet

## Titre

Modélisation, simulation et optimisation du transport d’un polluant atmosphérique en milieu urbain

## Question centrale

Comment le vent transporte-t-il un polluant depuis une source extérieure vers une zone urbaine, et comment une zone absorbante peut-elle réduire l’exposition de la population ?

## Étape 1 — Diffusion

État : code disponible, exécution à réaliser.

- équation de diffusion en deux dimensions ;
- différences finies ;
- condition de stabilité ;
- conservation de la masse ;
- étude du raffinement de la grille.

## Étape 2 — Transport par le vent

État : code et documentation disponibles, exécution à réaliser.

- ajout du terme d’advection ;
- comparaison de plusieurs directions et vitesses ;
- étude des oscillations numériques ;
- choix d’un schéma préservant la positivité.

## Étape 3 — Source et zone absorbante

- émission continue ou temporaire ;
- terme de disparition ;
- représentation d’une ceinture végétale ;
- comparaison avec et sans zone absorbante.

## Étape 4 — Mesures bruitées

- placement de capteurs ;
- production de séries temporelles ;
- ajout d’un bruit de mesure ;
- filtrage et reconstruction du champ de concentration.

## Étape 5 — Problème inverse

- estimation de la position de la source ;
- estimation de l’intensité de l’émission ;
- fonction de coût ;
- méthode d’optimisation ;
- analyse de sensibilité.

## Étape 6 — Optimisation environnementale

- position de la zone absorbante ;
- largeur et intensité d’absorption ;
- réduction de l’exposition urbaine ;
- comparaison du coût et de l’efficacité.

## Contrôles scientifiques

- stabilité ;
- convergence ;
- positivité ;
- conservation de masse ;
- reproductibilité ;
- comparaison avec un cas analytique ou une solution de référence ;
- limites du modèle.
