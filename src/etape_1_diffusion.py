"""Étape 1 : diffusion bidimensionnelle d'un polluant sans vent.

Le programme résout l'équation de diffusion sur un domaine carré avec des
frontières sans flux. Il produit des cartes de concentration, une animation
et un contrôle de conservation de la masse totale.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def lire_arguments() -> argparse.Namespace:
    """Lit les paramètres fournis dans la ligne de commande."""

    analyseur = argparse.ArgumentParser(
        description="Simuler la diffusion 2D d'un polluant sans vent."
    )
    analyseur.add_argument(
        "--taille",
        type=int,
        default=121,
        help="Nombre de points dans chaque direction.",
    )
    analyseur.add_argument(
        "--longueur",
        type=float,
        default=100.0,
        help="Longueur du domaine en kilomètres.",
    )
    analyseur.add_argument(
        "--duree",
        type=float,
        default=12.0,
        help="Durée simulée en heures.",
    )
    analyseur.add_argument(
        "--diffusion",
        type=float,
        default=5.0,
        help="Coefficient de diffusion en kilomètres carrés par heure.",
    )
    analyseur.add_argument(
        "--securite",
        type=float,
        default=0.90,
        help="Facteur de sécurité pour la condition de stabilité.",
    )
    analyseur.add_argument(
        "--sortie",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "resultats",
        help="Dossier dans lequel enregistrer les résultats.",
    )
    return analyseur.parse_args()


def verifier_arguments(arguments: argparse.Namespace) -> None:
    """Vérifie la cohérence des paramètres numériques."""

    if arguments.taille < 21:
        raise ValueError("La taille de la grille doit être au moins égale à 21.")
    if arguments.longueur <= 0.0:
        raise ValueError("La longueur du domaine doit être positive.")
    if arguments.duree <= 0.0:
        raise ValueError("La durée doit être positive.")
    if arguments.diffusion <= 0.0:
        raise ValueError("Le coefficient de diffusion doit être positif.")
    if not 0.0 < arguments.securite <= 1.0:
        raise ValueError("Le facteur de sécurité doit appartenir à ]0, 1].")


def concentration_initiale(
    x: np.ndarray,
    y: np.ndarray,
    longueur: float,
) -> np.ndarray:
    """Construit une tache gaussienne puis normalise sa masse à une unité."""

    centre_x = 0.25 * longueur
    centre_y = 0.50 * longueur
    largeur = 0.045 * longueur

    concentration = np.exp(
        -(
            (x - centre_x) ** 2
            + (y - centre_y) ** 2
        )
        / (2.0 * largeur**2)
    )
    return concentration


def laplacien_sans_flux(
    concentration: np.ndarray,
    pas_espace: float,
) -> np.ndarray:
    """Calcule le laplacien à cinq points avec des frontières sans flux."""

    prolongee = np.pad(concentration, 1, mode="edge")
    voisins = (
        prolongee[2:, 1:-1]
        + prolongee[:-2, 1:-1]
        + prolongee[1:-1, 2:]
        + prolongee[1:-1, :-2]
    )
    centre = 4.0 * prolongee[1:-1, 1:-1]
    return (voisins - centre) / (pas_espace**2)


def masse_totale(
    concentration: np.ndarray,
    pas_espace: float,
) -> float:
    """Approche l'intégrale de la concentration sur le domaine."""

    return float(np.sum(concentration) * pas_espace**2)


def instants_a_sauvegarder(
    nombre_etapes: int,
) -> list[int]:
    """Choisit quatre instants représentatifs de la simulation."""

    indices = {
        0,
        nombre_etapes // 3,
        2 * nombre_etapes // 3,
        nombre_etapes,
    }
    return sorted(indices)


def simuler(
    concentration_depart: np.ndarray,
    coefficient_diffusion: float,
    pas_espace: float,
    pas_temps: float,
    nombre_etapes: int,
) -> tuple[list[np.ndarray], list[float], list[float], list[np.ndarray]]:
    """Effectue la simulation et conserve les contrôles numériques."""

    concentration = concentration_depart.copy()
    temps = [0.0]
    masses = [masse_totale(concentration, pas_espace)]
    images_animation = [concentration.copy()]

    indices_images = set(instants_a_sauvegarder(nombre_etapes))
    instantanes: list[np.ndarray] = [concentration.copy()]

    frequence_animation = max(1, nombre_etapes // 100)

    for etape in range(1, nombre_etapes + 1):
        concentration += (
            coefficient_diffusion
            * pas_temps
            * laplacien_sans_flux(concentration, pas_espace)
        )

        temps.append(etape * pas_temps)
        masses.append(masse_totale(concentration, pas_espace))

        if etape in indices_images:
            instantanes.append(concentration.copy())

        if etape % frequence_animation == 0 or etape == nombre_etapes:
            images_animation.append(concentration.copy())

    return instantanes, temps, masses, images_animation


def enregistrer_instantanes(
    instantanes: list[np.ndarray],
    duree_reelle: float,
    longueur: float,
    sortie: Path,
) -> None:
    """Produit une figure contenant quatre cartes de concentration."""

    figure, axes = plt.subplots(2, 2, figsize=(11, 9))
    valeurs_temps = np.linspace(0.0, duree_reelle, len(instantanes))
    maximum = max(float(np.max(image)) for image in instantanes)

    for axe, image, temps in zip(axes.flat, instantanes, valeurs_temps):
        affichage = axe.imshow(
            image,
            origin="lower",
            extent=[0.0, longueur, 0.0, longueur],
            cmap="inferno",
            vmin=0.0,
            vmax=maximum,
        )
        axe.set_title(f"t = {temps:.2f} h")
        axe.set_xlabel("x (km)")
        axe.set_ylabel("y (km)")
        figure.colorbar(affichage, ax=axe, fraction=0.046, pad=0.04)

    figure.suptitle("Diffusion bidimensionnelle du polluant", fontsize=15)
    figure.tight_layout()
    figure.savefig(
        sortie / "diffusion_instants.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


def enregistrer_masse(
    temps: list[float],
    masses: list[float],
    sortie: Path,
) -> None:
    """Enregistre la courbe et les valeurs de conservation de la masse."""

    figure, axe = plt.subplots(figsize=(8, 4.5))
    axe.plot(temps, masses, color="#176B87", linewidth=2.0)
    axe.set_title("Contrôle de la masse totale")
    axe.set_xlabel("Temps (h)")
    axe.set_ylabel("Masse totale")
    axe.grid(alpha=0.3)
    figure.tight_layout()
    figure.savefig(
        sortie / "conservation_masse.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)

    with (sortie / "conservation_masse.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as fichier:
        redacteur = csv.writer(fichier)
        redacteur.writerow(["temps_heures", "masse_totale"])
        redacteur.writerows(zip(temps, masses))


def enregistrer_animation(
    images: list[np.ndarray],
    duree_reelle: float,
    longueur: float,
    sortie: Path,
) -> None:
    """Crée une animation GIF de l'évolution de la concentration."""

    figure, axe = plt.subplots(figsize=(6.5, 5.5))
    maximum = float(np.max(images[0]))
    affichage = axe.imshow(
        images[0],
        origin="lower",
        extent=[0.0, longueur, 0.0, longueur],
        cmap="inferno",
        vmin=0.0,
        vmax=maximum,
    )
    titre = axe.set_title("t = 0.00 h")
    axe.set_xlabel("x (km)")
    axe.set_ylabel("y (km)")
    figure.colorbar(affichage, ax=axe, label="Concentration")

    def mettre_a_jour(numero: int) -> tuple[object, object]:
        affichage.set_data(images[numero])
        temps = duree_reelle * numero / max(1, len(images) - 1)
        titre.set_text(f"t = {temps:.2f} h")
        return affichage, titre

    film = animation.FuncAnimation(
        figure,
        mettre_a_jour,
        frames=len(images),
        interval=80,
        blit=False,
    )
    film.save(sortie / "diffusion.gif", writer="pillow", fps=12)
    plt.close(figure)


def enregistrer_bilan(
    sortie: Path,
    arguments: argparse.Namespace,
    pas_espace: float,
    pas_temps: float,
    nombre_etapes: int,
    masses: list[float],
    concentration_finale: np.ndarray,
) -> None:
    """Enregistre les paramètres et les principaux contrôles."""

    masse_depart = masses[0]
    masse_fin = masses[-1]
    erreur_relative_masse = abs(masse_fin - masse_depart) / masse_depart

    lignes = [
        "Bilan de l'étape 1 — diffusion sans vent",
        "",
        f"Taille de la grille : {arguments.taille} x {arguments.taille}",
        f"Longueur du domaine : {arguments.longueur:.6f} km",
        f"Coefficient de diffusion : {arguments.diffusion:.6f} km²/h",
        f"Pas d'espace : {pas_espace:.8f} km",
        f"Pas de temps : {pas_temps:.8f} h",
        f"Nombre d'étapes : {nombre_etapes}",
        f"Durée réellement simulée : {nombre_etapes * pas_temps:.8f} h",
        f"Masse initiale : {masse_depart:.12e}",
        f"Masse finale : {masse_fin:.12e}",
        f"Erreur relative de masse : {erreur_relative_masse:.12e}",
        f"Concentration minimale finale : {np.min(concentration_finale):.12e}",
        f"Concentration maximale finale : {np.max(concentration_finale):.12e}",
        "",
        "Le résultat est acceptable si la concentration reste positive et si",
        "l'erreur relative de masse reste proche de la précision numérique.",
    ]

    (sortie / "bilan.txt").write_text(
        "\n".join(lignes) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Lance l'expérience complète."""

    arguments = lire_arguments()
    verifier_arguments(arguments)
    arguments.sortie.mkdir(parents=True, exist_ok=True)

    pas_espace = arguments.longueur / (arguments.taille - 1)
    pas_temps_maximal = pas_espace**2 / (4.0 * arguments.diffusion)
    pas_temps = arguments.securite * pas_temps_maximal
    nombre_etapes = math.ceil(arguments.duree / pas_temps)
    pas_temps = arguments.duree / nombre_etapes

    axe = np.linspace(0.0, arguments.longueur, arguments.taille)
    x, y = np.meshgrid(axe, axe)

    depart = concentration_initiale(x, y, arguments.longueur)
    depart /= masse_totale(depart, pas_espace)

    instantanes, temps, masses, images_animation = simuler(
        depart,
        arguments.diffusion,
        pas_espace,
        pas_temps,
        nombre_etapes,
    )

    enregistrer_instantanes(
        instantanes,
        nombre_etapes * pas_temps,
        arguments.longueur,
        arguments.sortie,
    )
    enregistrer_masse(temps, masses, arguments.sortie)
    enregistrer_animation(
        images_animation,
        nombre_etapes * pas_temps,
        arguments.longueur,
        arguments.sortie,
    )
    enregistrer_bilan(
        arguments.sortie,
        arguments,
        pas_espace,
        pas_temps,
        nombre_etapes,
        masses,
        instantanes[-1],
    )

    erreur_masse = abs(masses[-1] - masses[0]) / masses[0]
    print(f"Natayij t7ettou f: {arguments.sortie.resolve()}")
    print(f"Lkhtaa nnisbi dyal lkammiya: {erreur_masse:.6e}")
    print(f"A9al tarkiz f nihaya: {np.min(instantanes[-1]):.6e}")


if __name__ == "__main__":
    main()
