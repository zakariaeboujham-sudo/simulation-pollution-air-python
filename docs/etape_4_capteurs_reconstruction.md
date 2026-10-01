# Étape 4 — Capteurs et reconstruction

La version exécutable se trouve dans src/etape_4_capteurs_reconstruction.py.
Elle échantillonne le solveur de l'étape 3, ajoute du bruit gaussien reproductible,
applique une moyenne mobile et reconstruit le champ par IDW. Voir
[completion.md](completion.md) pour les conventions et limites temporelles.

~~~powershell
python src/etape_4_capteurs_reconstruction.py --taille 41 --duree 24 --capteurs-x 5 --capteurs-y 5 --bruit 5 --fenetre-filtrage 5 --graine 2026
~~~

Le niveau de bruit est un pourcentage du maximum exact mesuré. Les mesures
négatives sont écrêtées à zéro. Le filtre est centré, hors ligne ; les fenêtres
paires ont un point de plus du côté passé. La reconstruction retrouve les valeurs
aux capteurs, mais ne connaît ni le vent ni la source. RMSE et MAE comparent
chaque reconstruction au champ de référence interpolé dans le temps.

Les sorties comprennent implantation_capteurs.png, series_capteurs.png,
reconstruction_champ.png, erreurs_reconstruction.png, trois CSV et
bilan.json. Le filtrage n'est pas supposé toujours améliorer l'erreur spatiale.
