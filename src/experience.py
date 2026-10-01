"""Outils communs aux experiences 4 a 6, avec le solveur conservatif existant."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np
from etape_3_source_absorption import simuler_scenario, masque_zone_urbaine


def arguments(etape):
    p = argparse.ArgumentParser(description=etape)
    p.add_argument('--taille', type=int, default=41)
    p.add_argument('--duree', type=float, default=24)
    p.add_argument('--graine', type=int, default=2026)
    p.add_argument('--bruit', type=float, default=5)
    p.add_argument('--capteurs-x', type=int, default=5)
    p.add_argument('--capteurs-y', type=int, default=5)
    p.add_argument('--fenetre-filtrage', type=int, default=5)
    p.add_argument('--pas-mesure', type=float, default=0.5)
    p.add_argument('--sortie', type=Path, default=Path(__file__).resolve().parents[1]/'resultats'/etape)
    a = p.parse_args()
    if (a.taille < 31 or not np.isfinite(a.duree) or a.duree <= 0
            or not np.isfinite(a.bruit) or a.bruit < 0
            or not np.isfinite(a.pas_mesure) or a.pas_mesure <= 0
            or a.fenetre_filtrage < 1
            or min(a.capteurs_x, a.capteurs_y) < 2
            or max(a.capteurs_x, a.capteurs_y) > a.taille):
        p.error('Parametres de grille, mesure ou duree invalides.')
    a.sortie.mkdir(parents=True, exist_ok=True)
    return a


def grille(n):
    h = 100/n
    x, y = np.meshgrid((np.arange(n)+0.5)*h, (np.arange(n)+0.5)*h)
    return x, y, h


def simuler(n=41, duree=24, position=(15, 50), emission=1, ceinture=(53, 7, .45), cfl=.9):
    x, y, h = grille(n)
    source = np.exp(-((x-position[0])**2+(y-position[1])**2)/(2*2.5**2))
    source /= source.sum()*h*h
    debut, largeur, taux = ceinture
    k = taux*((x >= debut)&(x <= debut+largeur)&(y >= 22)&(y <= 78))
    return simuler_scenario('Experience', source, masque_zone_urbaine(x,y,100),
                            k, h, duree, 18, emission, 1.5, 3, .3, .85, cfl)


def capteurs(n, nx=5, ny=5):
    ix = np.linspace(0,n-1,nx).round().astype(int)
    iy = np.linspace(0,n-1,ny).round().astype(int)
    xx, yy = np.meshgrid(ix,iy)
    return yy.ravel(), xx.ravel()


def mesures(resultat, indices, pas=.5):
    # Interpolation temporelle des champs conserves par le solveur (environ 100).
    t = np.arange(0,resultat.temps[-1],pas)
    t = np.append(t,resultat.temps[-1])
    valeurs = np.array([c[indices] for c in resultat.images_animation])
    return t, np.array([np.interp(t,resultat.temps_animation,v) for v in valeurs.T]).T


def filtrer(v, fenetre):
    # Moyenne centree hors ligne ; les bords utilisent uniquement les points disponibles.
    rayon = fenetre//2
    return np.array([v[max(0,i-rayon):min(len(v),i+(fenetre-rayon))].mean(axis=0)
                     for i in range(len(v))])


def poids_idw(n, indices):
    yy, xx = np.indices((n,n))
    d2 = (yy.ravel()[:,None]-indices[0])**2+(xx.ravel()[:,None]-indices[1])**2
    w = 1/np.maximum(d2,1e-20)
    w /= w.sum(axis=1,keepdims=True)
    return w


def csv_ecrire(path, entetes, lignes):
    with path.open('w',newline='',encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(entetes); w.writerows(lignes)


def bilan(path, contenu):
    path.write_text(json.dumps(contenu,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
