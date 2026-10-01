# Vérification de la version complétée

Source : archive de la branche main du dépôt
zakariaeboujham-sudo/simulation-pollution-air-python, commit annoncé c569dc3,
récupérée le 1 octobre 2026. L'archive contenait les scripts 1 à 3, mais pas
le script 4, les tests ni le workflow annoncés par le README.

## Exécution locale

Python 3.12, NumPy 2.3.5, Matplotlib 3.11.2. La commande python lancer.py
a exécuté les étapes 3 à 6 jusqu'au bout. Six tests scientifiques passent
avec unittest. Les résultats sont régénérés dans resultats/ par le lanceur.
Les étapes 1 et 2 ont également été exécutées avec une grille 31 × 31 et une
durée de 2 h, figures et GIF compris : erreur relative de masse nulle pour
l'étape 1 et centre final (25,998 ; 51,600) km pour le vent oblique de l'étape 2.

Pour la grille 41 × 41 et la durée 24 h :

| Expérience | Résultat |
|---|---:|
| Étape 3, réduction d'exposition par la ceinture initiale | 51,71 % |
| Étape 3, erreur maximale de bilan de masse | 2,309 × 10⁻¹⁴ |
| Étape 4, RMSE finale IDW brute | 0,00196095 |
| Étape 4, RMSE finale IDW filtrée | 0,00179789 |
| Étape 5, position estimée | (15 ; 50) km |
| Étape 5, émission estimée / vraie | 1,40321 / 1,4 |
| Étape 6, ceinture retenue (début ; largeur ; absorption) | (40 km ; 10 km ; 0,9 h⁻¹) |
| Étape 6, réduction d'exposition | 88,80 % |

La figure de reconstruction a été inspectée visuellement. Elle montre aussi
le biais spatial de l'IDW lorsque les capteurs couvrent mal le maximum du panache.
Le filtrage réduit ici la RMSE mais ne supprime pas ce biais.

Les tests de conservation et de positivité ne suffisent pas à démontrer la
convergence du modèle. Les résultats ne constituent pas une prévision sanitaire
ou une validation d'une ceinture végétale réelle. Voir completion.md.

Les versions Python 3.10 et 3.11 sont prévues dans le workflow, mais n'ont pas
été exécutées localement. Cette version a été publiée sur main via l'éditeur web
GitHub. Les figures et GIF sont des sorties générées, non versionnées dans le dépôt.
