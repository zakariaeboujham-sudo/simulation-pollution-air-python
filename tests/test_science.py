import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experience import simuler, capteurs, poids_idw, filtrer
from etape_3_source_absorption import laplacien_sans_flux, divergence_advection_sans_flux
from etape_5_probleme_inverse import estimer


class Science(unittest.TestCase):
    def test_flux_conservatifs(self):
        c = np.random.default_rng(42).random((31,31))
        for u,v in [(3,.3),(-3,-.3),(0,0)]:
            self.assertAlmostEqual(divergence_advection_sans_flux(c,1,u,v).sum(),0,places=11)
        self.assertAlmostEqual(laplacien_sans_flux(c,1).sum(),0,places=11)

    def test_bilan_positivite_et_emission_partielle(self):
        r = simuler(31,19.13)
        self.assertGreaterEqual(min(r.minimums),-1e-12)
        self.assertAlmostEqual(r.emissions_cumulees[-1],18,places=10)
        self.assertLess(max(abs(e) for e in r.erreurs_bilan),1e-10)

    def test_absorption_diminue_exposition(self):
        sans = simuler(31,24,ceinture=(53,7,0))
        avec = simuler(31,24)
        self.assertGreater(sans.expositions_urbaines[-1],0)
        self.assertLess(avec.expositions_urbaines[-1],sans.expositions_urbaines[-1])

    def test_idw_exact_aux_capteurs_et_champ_constant(self):
        ij = capteurs(31)
        w = poids_idw(31,ij)
        v = np.arange(len(ij[0]))
        recon = (w@v).reshape(31,31)
        np.testing.assert_allclose(recon[ij],v,atol=1e-12)
        np.testing.assert_allclose(w@np.ones(len(v)),1)

    def test_filtre_constant_et_fenetre_paire(self):
        np.testing.assert_allclose(filtrer(np.ones((8,3)),4),1)
        np.testing.assert_allclose(filtrer(np.arange(4)[:,None],2).ravel(),[0,.5,1.5,2.5])

    def test_inverse_identifie_source_et_intensite(self):
        a = np.array([[1.,2.],[3.,4.]])
        b = np.array([[4.,1.],[2.,1.]])
        meilleur,_ = estimer(1.4*a,[((10,40),b),((15,50),a)])
        self.assertEqual(meilleur[:2],(15,50))
        self.assertAlmostEqual(meilleur[2],1.4)
        self.assertLess(meilleur[3],1e-25)


if __name__ == '__main__': unittest.main()
