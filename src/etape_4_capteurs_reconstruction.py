"""Mesures synthetiques, filtrage et reconstruction IDW."""
import numpy as np
import matplotlib.pyplot as plt
from experience import arguments, simuler, capteurs, mesures, filtrer, poids_idw, csv_ecrire, bilan


def main():
    a = arguments('etape_4')
    r = simuler(a.taille,a.duree)
    ij = capteurs(a.taille,a.capteurs_x,a.capteurs_y)
    t, exact = mesures(r,ij,a.pas_mesure)
    sigma = a.bruit/100*exact.max()
    brut = np.maximum(0,exact+np.random.default_rng(a.graine).normal(0,sigma,exact.shape))
    filtre = filtrer(brut,a.fenetre_filtrage)
    w = poids_idw(a.taille,ij)
    rb, rf = brut@w.T, filtre@w.T
    images = np.asarray(r.images_animation).reshape(len(r.images_animation),-1)
    reference = np.array([np.interp(t,r.temps_animation,v) for v in images.T]).T
    eb, ef = rb-reference, rf-reference
    rmse = lambda e: np.sqrt(np.mean(e**2,axis=1))
    mae = lambda e: np.mean(abs(e),axis=1)
    csv_ecrire(a.sortie/'diagnostics_reconstruction.csv',['temps_h','rmse_brut','rmse_filtre','mae_brut','mae_filtre'],zip(t,rmse(eb),rmse(ef),mae(eb),mae(ef)))
    csv_ecrire(a.sortie/'positions_capteurs.csv',['capteur','x_km','y_km','colonne','ligne'],[(i,(x+.5)*100/a.taille,(y+.5)*100/a.taille,x,y) for i,(y,x) in enumerate(zip(*ij))])
    csv_ecrire(a.sortie/'mesures_capteurs.csv',['temps_h','capteur','exact','brut','filtre'],[(tt,j,exact[i,j],brut[i,j],filtre[i,j]) for i,tt in enumerate(t) for j in range(exact.shape[1])])
    fig, axes = plt.subplots(1,4,figsize=(16,4),layout='constrained')
    vmax = max(reference[-1].max(),rb[-1].max(),rf[-1].max())
    for ax,c,titre in zip(axes,[reference[-1],rb[-1],rf[-1],abs(ef[-1])],['Reference','IDW brut','IDW filtre','Erreur absolue filtree']):
        im = ax.imshow(c.reshape(a.taille,a.taille),origin='lower',extent=[0,100,0,100],vmin=0,vmax=vmax if ax is not axes[-1] else None)
        ax.set_title(titre); fig.colorbar(im,ax=ax)
    fig.savefig(a.sortie/'reconstruction_champ.png'); plt.close(fig)
    fig,ax = plt.subplots(); ax.plot(t,rmse(eb),label='Brut'); ax.plot(t,rmse(ef),label='Filtre'); ax.set(xlabel='Temps (h)',ylabel='RMSE'); ax.legend(); fig.savefig(a.sortie/'erreurs_reconstruction.png'); plt.close(fig)
    fig,ax = plt.subplots(); ax.scatter((ij[1]+.5)*100/a.taille,(ij[0]+.5)*100/a.taille); ax.set(xlim=(0,100),ylim=(0,100),xlabel='x (km)',ylabel='y (km)'); fig.savefig(a.sortie/'implantation_capteurs.png'); plt.close(fig)
    fig,axes = plt.subplots(2,2,figsize=(10,6),layout='constrained')
    for ax,j in zip(axes.flat,np.linspace(0,exact.shape[1]-1,4).astype(int)):
        for v,nom in [(exact,'Exact'),(brut,'Brut'),(filtre,'Filtre')]: ax.plot(t,v[:,j],label=nom)
        ax.set_title(f'Capteur {j}'); ax.set_xlabel('Temps (h)'); ax.legend()
    fig.savefig(a.sortie/'series_capteurs.png'); plt.close(fig)
    bilan(a.sortie/'bilan.json',{'parametres':vars(a)|{'sortie':str(a.sortie)},'sigma':float(sigma),'rmse_finale_brute':float(rmse(eb)[-1]),'rmse_finale_filtree':float(rmse(ef)[-1]),'limite':'Mesures synthetiques ; interpolation temporelle des champs sauvegardes. Le filtrage ne garantit pas une meilleure reconstruction.'})
    print(f'Resultats : {a.sortie}')


if __name__ == '__main__': main()
