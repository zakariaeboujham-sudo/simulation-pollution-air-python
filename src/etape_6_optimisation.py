"""Comparaison exhaustive de ceintures avec cout conventionnel explicite."""
import matplotlib.pyplot as plt
from experience import arguments, simuler, csv_ecrire, bilan


def main():
    a = arguments('etape_6')
    reference = simuler(a.taille,a.duree,ceinture=(53,7,0)).expositions_urbaines[-1]
    if reference <= 1e-12:
        raise ValueError('Exposition de reference trop faible : augmenter la duree.')
    lignes = []
    for x in [40,50,60]:
        for largeur in [5,10]:
            for k in [.2,.45,.9]:
                r = simuler(a.taille,a.duree,ceinture=(x,largeur,k))
                ratio = r.expositions_urbaines[-1]/reference
                cout = largeur*k/(10*.9)
                score = ratio+.15*cout
                lignes.append((x,largeur,k,100*(1-ratio),cout,score,r.expositions_urbaines[-1]))
    meilleur = min(lignes,key=lambda row:row[5])
    csv_ecrire(a.sortie/'comparaison_ceintures.csv',['x_km','largeur_km','absorption_h-1','reduction_pct','cout_relatif','score','exposition'],lignes)
    bilan(a.sortie/'bilan.json',{'exposition_reference':reference,'meilleure_configuration':dict(zip(['x','largeur','absorption','reduction_pct','cout_relatif','score','exposition'],meilleur)),'objectif':'exposition / exposition_reference + 0.15 * largeur * absorption / 9','limites':'Optimum parmi 18 configurations seulement. Cout sans unite, convention pedagogique sans donnees economiques. Absorption simplifiee, sans validation du comportement reel de vegetaux.'})
    fig,ax = plt.subplots(); ax.scatter([r[4] for r in lignes],[r[3] for r in lignes]); ax.scatter(meilleur[4],meilleur[3],marker='*',s=180,label='Score minimal'); ax.set(xlabel='Cout relatif conventionnel',ylabel="Reduction de l'exposition (%)"); ax.legend(); fig.savefig(a.sortie/'cout_efficacite.png'); plt.close(fig)
    print(f'Meilleure ceinture (x,largeur,k) : {meilleur[:3]} ; reduction {meilleur[3]:.2f} %')


if __name__ == '__main__': main()
