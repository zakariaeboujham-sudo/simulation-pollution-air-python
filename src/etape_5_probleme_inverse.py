"""Recherche discrete de position et estimation lineaire de l'emission."""
import numpy as np
from experience import arguments, simuler, capteurs, mesures, csv_ecrire, bilan


def estimer(observe, candidats):
    lignes = []
    for position, prediction in candidats:
        denom = float(np.sum(prediction**2))
        q = max(0,float(np.sum(prediction*observe))/denom) if denom > 0 else 0
        cout = float(np.mean((q*prediction-observe)**2))
        lignes.append((*position,q,cout))
    return min(lignes,key=lambda r:r[-1]), lignes


def main():
    a = arguments('etape_5')
    ij = capteurs(a.taille,a.capteurs_x,a.capteurs_y)
    _, exact = mesures(simuler(a.taille,a.duree,emission=1.4),ij,a.pas_mesure)
    # Bruit signe conserve pour eviter le biais de l'ecretage dans l'estimation.
    observe = exact+np.random.default_rng(a.graine).normal(0,a.bruit/100*exact.max(),exact.shape)
    candidats = [((x,y),mesures(simuler(a.taille,a.duree,(x,y)),ij,a.pas_mesure)[1]) for x in [10,15,20,25] for y in [40,45,50,55,60]]
    meilleur,lignes = estimer(observe,candidats)
    csv_ecrire(a.sortie/'candidats.csv',['x_km','y_km','emission','cout_mse'],lignes)
    bilan(a.sortie/'bilan.json',{'source_vraie':[15,50,1.4],'source_estimee':meilleur[:3],'cout':meilleur[3],'limites':'Recherche sur 20 positions seulement ; vent, diffusion et absorption supposes connus. Donnees synthetiques issues du meme modele, sans validation sur mesures reelles.'})
    print(f'Source estimee (x,y,emission) : {meilleur[:3]}')


if __name__ == '__main__': main()
