# Étape 2 — Transport du polluant par le vent

## Objectif

Cette étape étudie simultanément deux phénomènes :

- la diffusion, qui étale le nuage de polluant dans toutes les directions ;
- l’advection, qui déplace ce nuage dans la direction du vent.

Le modèle résout l’équation d’advection-diffusion

    ∂c/∂t + u ∂c/∂x + v ∂c/∂y = D Δc,

où `c` est la concentration, `(u, v)` la vitesse du vent et `D` le coefficient de diffusion.

## Choix numérique

Le temps est avancé avec Euler explicite. Le laplacien est calculé par différences finies centrées. Les dérivées d’advection utilisent un schéma amont : l’information est prise du côté d’où vient le vent.

Ce choix est moins précis qu’un schéma d’ordre élevé, mais il est robuste, simple à interpréter et préserve la positivité lorsque le pas de temps satisfait la condition de stabilité.

Le programme impose

    Δt ≤ sécurité / ((|u| + |v|)/Δx + 4D/Δx²).

## Expériences comparées

Trois scénarios partent exactement du même nuage initial :

1. sans vent : seule la diffusion agit ;
2. vent horizontal : le nuage se déplace vers l’est ;
3. vent oblique : le nuage se déplace vers l’est et vers le nord.

La position moyenne du nuage est suivie par son centre de masse. Cette mesure permet de séparer visuellement et quantitativement le déplacement produit par le vent de l’étalement produit par la diffusion.

## Résultats attendus

- sans vent, le centre du nuage doit rester presque immobile ;
- avec un vent horizontal positif, sa coordonnée `x` doit augmenter ;
- avec un vent oblique positif, ses coordonnées `x` et `y` doivent augmenter ;
- la concentration minimale doit rester positive ou très proche de zéro ;
- la variation de masse doit rester faible tant que le nuage reste loin des frontières.

Ces conclusions sont des critères de contrôle. Elles ne doivent être présentées comme résultats obtenus qu’après exécution du programme.

## Fichiers produits

- `transport_instants.png` : évolution du scénario principal ;
- `comparaison_scenarios.png` : concentrations finales des trois vents ;
- `trajectoires_centres.png` : déplacement du centre du nuage ;
- `transport_vent.gif` : animation du transport ;
- `diagnostics.csv` : valeurs numériques à analyser ;
- `bilan.txt` : résumé des paramètres et contrôles.
