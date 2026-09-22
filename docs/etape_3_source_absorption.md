# Étape 3 — Source continue et zone absorbante

## Objectif

Cette étape étudie l'effet d'une ceinture absorbante placée entre une source de pollution et une zone urbaine. Deux simulations sont comparées avec les mêmes paramètres : l'une sans barrière, l'autre avec barrière.

## Modèle mathématique

Le champ de concentration `c(x, y, t)` vérifie

    ∂c/∂t + u ∂c/∂x + v ∂c/∂y = D Δc + S(x, y, t) - k(x, y)c.

- `D` est le coefficient de diffusion en km²/h ;
- `(u, v)` est la vitesse constante du vent en km/h ;
- `S` est une source gaussienne normalisée, active pendant une durée réglable ;
- `k` est nul hors de la barrière et positif à l'intérieur.

L'intensité passée avec `--intensite-source` représente ainsi une masse injectée par heure, indépendamment du maillage.

## Discrétisation

Le temps est avancé avec Euler explicite. La diffusion utilise un laplacien centré à cinq points et l'advection un schéma amont. Le pas de temps satisfait

    Δt ≤ sécurité / ((|u| + |v|)/Δx + 4D/Δx² + max(k)).

Cette condition rend tous les coefficients explicites non négatifs et permet de contrôler la positivité de la concentration. Les deux scénarios utilisent le même pas de temps afin que la comparaison ne soit pas influencée par la discrétisation temporelle.

## Indicateurs

Le programme calcule à chaque pas :

- la masse présente dans le domaine ;
- la masse émise cumulée ;
- la masse absorbée cumulée ;
- la masse instantanée située dans la zone urbaine ;
- l'exposition urbaine cumulée, intégrale temporelle de cette masse ;
- la concentration minimale, utilisée comme contrôle de positivité.

Le bilan `masse émise - masse absorbée - masse présente` est attribué aux échanges numériques avec les frontières. Il devient particulièrement important lorsque le panache atteint la limite du domaine.

## Exécution

Installation :

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

Simulation complète :

~~~powershell
python src\etape_3_source_absorption.py
~~~

Calcul rapide sans animation :

~~~powershell
python src\etape_3_source_absorption.py --taille 61 --duree 6 --sans-animation
~~~

Tests :

~~~powershell
python -m unittest discover -s tests -v
~~~

## Fichiers produits

- `source_absorption_instants.png` : quatre instants du scénario avec barrière ;
- `comparaison_absorption.png` : champs finaux avec la même échelle ;
- `evolution_indicateurs.png` : masses, exposition urbaine et absorption ;
- `source_absorption.gif` : évolution du scénario avec barrière ;
- `diagnostics.csv` : séries temporelles des deux expériences ;
- `bilan.txt` : paramètres, bilans de masse et réduction d'exposition.

## Interprétation prudente

Une réduction positive de l'exposition urbaine signifie que la barrière retire une partie du panache avant son arrivée dans la ville pour les paraiètres choisis. Elle ne constitue pas, à elle seule, une validation pour une situation réelle : le vent variable, la topographie, la turbulence, la chimie atmosphérique et la capacité réelle de la végétation ne sont pas encore représentés.
