# Base simple et limites scientifiques

La question est : comment une source polluante expose-t-elle une ville et quelle
ceinture absorbante permet de diminuer cette exposition ? Les étapes 1 à 3
introduisent les mécanismes physiques. Les étapes 4 à 6 ajoutent observation,
identification et décision. Elles réutilisent le solveur conservatif de l'étape 3.

## Hypothèses communes

Domaine carré de 100 km, temps en heures, vent constant (3 ; 0,3) km/h,
diffusion 1,5 km²/h, source gaussienne de largeur 2,5 km, active pendant 18 h.
La masse reste en unité arbitraire ; la concentration est en unité de masse/km².
Les frontières sont fermées : le polluant s'accumule aux bords. Cela permet le
contrôle du bilan, mais limite l'interprétation atmosphérique sur de longues durées.
Le pas CFL combiné assure la positivité du schéma explicite. Les comparaisons
utilisent une borne d'absorption commune de 0,9 h⁻¹ pour conserver le même pas.

## Étape 4

Capteurs aux centres des cellules, bruit gaussien reproductible, écrêtage à zéro,
moyenne mobile centrée et IDW de puissance 2. Le filtre est hors ligne et utilise
des mesures futures. Les séries et champs de référence sont interpolés dans le
temps depuis environ 100 sauvegardes du solveur : diminuer le pas de mesure ne
crée pas de nouvelle résolution temporelle. RMSE et MAE portent sur le domaine
entier. Une baisse du bruit ne garantit pas une baisse de l'erreur spatiale.

## Étape 5

On teste 20 positions, x dans {10,15,20,25}, y dans {40,45,50,55,60} km.
Pour chaque simulation à émission unitaire p, la linéarité donne l'émission
q = max(0, somme(p*m)/somme(p²)). La position minimise la moyenne des résidus
quadratiques. Les observations synthétiques proviennent de (15,50), émission
1,4, et conservent le bruit signé pour éviter le biais d'écrêtage.
L'identification suppose connus le vent, la diffusion et la ceinture. Une source
hors de la grille ne peut être retrouvée exactement. Un ajustement synthétique
avec le même modèle ne constitue pas une validation sur le terrain.

## Étape 6

18 ceintures : positions {40,50,60} km, largeurs {5,10} km, absorptions
{0,2 ; 0,45 ; 0,9} h⁻¹. La hauteur reste fixée à 56 km.
Le score vaut exposition/exposition_sans_ceinture + 0,15 * largeur * absorption/9.
Le coût est une convention pédagogique, sans prix réel. Le meilleur score
désigne uniquement le meilleur candidat de cette liste, sous ces hypothèses.
Une durée trop courte pour exposer la ville est refusée.

## Contrôles et suites possibles

Les tests vérifient les flux conservatifs, le bilan émission-absorption-masse,
la positivité, l'exposition réduite, l'interpolation aux capteurs et l'estimation
linéaire. Le maillage doit encore faire l'objet d'une étude systématique de
convergence pour une exploitation quantitative. La diffusion numérique amont,
les frontières fermées, l'absence de météorologie variable et de données réelles
doivent accompagner toute conclusion environnementale.
