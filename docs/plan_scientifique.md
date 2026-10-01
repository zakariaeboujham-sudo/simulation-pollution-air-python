# Plan scientifique du projet

## Titre

Modélisation, simulation et optimisation du transport d’un polluant atmosphérique en milieu urbain

## Question centrale

Comment le vent transporte-t-il un polluant depuis une source extérieure vers une zone urbaine, et comment une zone absorbante peut-elle réduire l’exposition de la population ?

## Étape 1 — Diffusion

État : code disponible et exécution rapide vérifiée ; convergence à étudier.

- équation de diffusion en deux dimensions ;
- différences finies ;
- condition de stabilité ;
- conservation de la masse ;
- étude du raffinement de la grille à poursuivre.

## Étape 2 — Transport par le vent

État : code et documentation disponibles, exécution rapide vérifiée.

- ajout du terme d’advection ;
- comparaison de plusieurs directions et vitesses ;
- étude des oscillations numériques ;
- choix d’un schéma préservant la positivité.

## Étape 3 — Source et zone absorbante

État : code, documentation et tests disponibles.

- émission continue ou temporaire ;
- terme de disparition ;
- représentation d’une ceinture végétale ;
- comparaison avec et sans zone absorbante ;
- suivi du bilan de masse et de l’exposition urbaine cumulée.

## Étape 4 — Mesures bruitées

État : code, documentation et tests disponibles.

- placement de capteurs ;
- production de séries temporelles ;
- ajout d’un bruit de mesure ;
- filtrage et reconstruction du champ de concentration ;
- comparaison quantitative par RMSE et MAE.

## Étape 5 — Problème inverse

État : recherche discrète et estimation linéaire disponibles et exécutées.

- estimation de la position de la source parmi 20 candidats ;
- estimation de l’intensité de l’émission par moindres carrés ;
- fonction de coût quadratique ;
- analyse de sensibilité approfondie à poursuivre.

## Étape 6 — Optimisation environnementale

État : comparaison de 18 configurations disponible et exécutée, avec coût conventionnel.

- position de la zone absorbante ;
- largeur et intensité d’absorption ;
- réduction de l’exposition urbaine ;
- comparaison du coût et de l’efficacité.

## Contrôles scientifiques

Stabilité CFL, positivité, conservation de masse et reproductibilité sont
contrôlées par le solveur et les tests. Convergence systématique, comparaison
analytique et validation sur des données réelles restent à approfondir.
Les méthodes, hypothèses et limites sont décrites dans [completion.md](completion.md).
