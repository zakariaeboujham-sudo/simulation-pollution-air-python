"""Lance la chaine simple 3 -> 4 -> 5 -> 6 depuis n'importe quel repertoire."""
import subprocess
import sys
from pathlib import Path

racine = Path(__file__).resolve().parent
for script, options in [
    ('etape_3_source_absorption.py',['--taille','41','--sans-animation']),
    ('etape_4_capteurs_reconstruction.py',[]),
    ('etape_5_probleme_inverse.py',[]),
    ('etape_6_optimisation.py',[]),
]:
    subprocess.run([sys.executable,str(racine/'src'/script),*options],check=True)
