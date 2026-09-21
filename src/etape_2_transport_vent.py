"""Étape 2 : transport d'un polluant par diffusion et par le vent.

Le programme résout une équation d'advection-diffusion en deux dimensions.
Le terme d'advection est discrétisé par un schéma amont, choisi pour éviter
les oscillations artificielles et préserver la positivité sous condition CFL.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class ResultatSimulation:
    """Regroupe les sorties nécessaires aux graphiques et aux contrôles."""

    nom: str
    vitesse_x: float
    vitesse_y: float
    temps: list[float]
    masses: list[float]
    minimums: list[float]
    centres_x: list[float]
    centres_y: list[float]
    instantanes: list[np.ndarray]
    temps_instantanes: list[float]
    images_animation: list[np.ndarray]


def lire_arguments() -> argparse.Namespace:
    """Lit les paramètres de la simulation."""

    analyseur = argparse.ArgumentParser(
        description="Simuler le transport 2D d'un polluant par le vent."
    )
    analyseur.add_argument("--taille", type=int, default=121)
    analyseur.add_argument("--longueur", type=float, default=100.0)
    analyseur.add_argument("--duree", type=float, default=10.0)
    analyseur.add_argument("--diffusion", type=float, default=1.5)
    analyseur.add_argument(
        "--vent-x",
        type=float,
        default=3.0,
        help="Composante est-ouest du vent en km/h.",
    )
    analyseur.add_argument(
        "--vent-y",
        type=float,
        default=0.8,
        help="Composante nord-sud du vent en km/h.",
    )
    analyseur.add_argument("--securite", type=float, default=0.85)
    analyseur.add_argument(
        "--sortie",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "resultats" / "etape_2",
    )
    return analyseur.parse_args()


def verifier_arguments(arguments: argparse.Namespace) -> None:
    """Refuse les paramètres qui ne définissent pas une expérience valide."""

    if arguments.taille < 21:
        raise ValueError("La grille doit contenir au moins 21 points par axe.")
    if arguments.longueur <= 0.0 or arguments.duree <= 0.0:
        raise ValueError("La longueur et la durée doivent être positives.")
    if arguments.diffusion <= 0.0:
        raise ValueError("Le coefficient de diffusion doit être positif.")
    if not 0.0 < arguments.securite <= 1.0:
        raise ValueError("Le facteur de sécurité doit appartenir à ]0, 1].")


def concentration_initiale(
    x: np.ndarray,
    y: np.ndarray,
    longueur: float,
) -> np.ndarray:
    """Crée un nuage gaussien localisé à l'ouest du domaine."""

    centre_x = 0.20 * longueur
    centre_y = 0.50 * longueur
    largeur = 0.045 * longueur
    return np.exp(
        -((x - centre_x) ** 2 + (y - centre_y) ** 2) / (2.0 * largeur**2)
    )


def masse_totale(concentration: np.ndarray, pas_espace: float) -> float:
    """Approche l'intégrale de la concentration sur le domaine."""

    return float(np.sum(concentration) * pas_espace**2)


def centre_de_masse(
    concentration: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float]:
    """Calcule la position moyenne du nuage de pollution."""

    poids = float(np.sum(concentration))
    if poids <= 0.0:
        return float("nan"), float("nan")
    centre_x = float(np.sum(x * concentration) / poids)
    centre_y = float(np.sum(y * concentration) / poids)
    return centre_x, centre_y


def laplacien_sans_flux(
    concentration: np.ndarray,
    pas_espace: float,
) -> np.ndarray:
    """Calcule le laplacien à cinq points avec frontières sans flux."""

    prolongee = np.pad(concentration, 1, mode="edge")
    voisins = (
        prolongee[2:, 1:-1]
        + prolongee[:-2, 1:-1]
        + prolongee[1:-1, 2:]
        + prolongee[1:-1, :-2]
    )
    centre = 4.0 * prolongee[1:-1, 1:-1]
    return (voisins - centre) / pas_espace**2


def gradients_amont(
    concentration: np.ndarray,
    pas_espace: float,
    vitesse_x: float,
    vitesse_y: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Approche les dérivées dans la direction d'où vient l'information."""

    prolongee = np.pad(concentration, 1, mode="edge")
    centre = prolongee[1:-1, 1:-1]

    if vitesse_x >= 0.0:
        derivee_x = (centre - prolongee[1:-1, :-2]) / pas_espace
    else:
        derivee_x = (prolongee[1:-1, 2:] - centre) / pas_espace

    if vitesse_y >= 0.0:
        derivee_y = (centre - prolongee[:-2, 1:-1]) / pas_espace
    else:
        derivee_y = (prolongee[2:, 1:-1] - centre) / pas_espace

    return derivee_x, derivee_y


def calculer_pas_temps(
    pas_espace: float,
    diffusion: float,
    vitesse_x: float,
    vitesse_y: float,
    securite: float,
) -> float:
    """Calcule un pas explicite satisfaisant advection et diffusion."""

    taux_advection = (abs(vitesse_x) + abs(vitesse_y)) / pas_espace
    taux_diffusion = 4.0 * diffusion / pas_espace**2
    return securite / (taux_advection + taux_diffusion)


def indices_instantanes(nombre_etapes: int) -> list[int]:
    """Sélectionne quatre instants représentatifs."""

    return sorted({0, nombre_etapes // 3, 2 * nombre_etapes // 3, nombre_etapes})


def simuler_scenario(
    nom: str,
    depart: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    pas_espace: float,
    duree: float,
    diffusion: float,
    vitesse_x: float,
    vitesse_y: float,
    securite: float,
) -> ResultatSimulation:
    """Résout l'équation d'advection-diffusion pour un vent constant."""

    pas_maximal = calculer_pas_temps(
        pas_espace,
        diffusion,
        vitesse_x,
        vitesse_y,
        securite,
    )
    nombre_etapes = math.ceil(duree / pas_maximal)
    pas_temps = duree / nombre_etapes
    choix_instantanes = set(indices_instantanes(nombre_etapes))
    frequence_animation = max(1, nombre_etapes // 100)

    concentration = depart.copy()
    centre_x, centre_y = centre_de_masse(concentration, x, y)
    temps = [0.0]
    masses = [masse_totale(concentration, pas_espace)]
    minimums = [float(np.min(concentration))]
    centres_x = [centre_x]
    centres_y = [centre_y]
    instantanes = [concentration.copy()]
    temps_instantanes = [0.0]
    images_animation = [concentration.copy()]

    for etape in range(1, nombre_etapes + 1):
        derivee_x, derivee_y = gradients_amont(
            concentration,
            pas_espace,
            vitesse_x,
            vitesse_y,
        )
        concentration = concentration + pas_temps * (
            diffusion * laplacien_sans_flux(concentration, pas_espace)
            - vitesse_x * derivee_x
            - vitesse_y * derivee_y
        )

        temps_actuel = etape * pas_temps
        centre_x, centre_y = centre_de_masse(concentration, x, y)
        temps.append(temps_actuel)
        masses.append(masse_totale(concentration, pas_espace))
        minimums.append(float(np.min(concentration)))
        centres_x.append(centre_x)
        centres_y.append(centre_y)

        if etape in choix_instantanes:
            instantanes.append(concentration.copy())
            temps_instantanes.append(temps_actuel)
        if etape % frequence_animation == 0 or etape == nombre_etapes:
            images_animation.append(concentration.copy())

    return ResultatSimulation(
        nom=nom,
        vitesse_x=vitesse_x,
        vitesse_y=vitesse_y,
        temps=temps,
        masses=masses,
        minimums=minimums,
        centres_x=centres_x,
        centres_y=centres_y,
        instantanes=instantanes,
        temps_instantanes=temps_instantanes,
        images_animation=images_animation,
    )


def enregistrer_instantanes(
    resultat: ResultatSimulation,
    longueur: float,
    sortie: Path,
) -> None:
    """Montre le déplacement et l'étalement du nuage sous le vent choisi."""

    figure, axes = plt.subplots(2, 2, figsize=(11, 9))
    maximum = max(float(np.max(image)) for image in resultat.instantanes)

    for axe, image, temps in zip(
        axes.flat,
        resultat.instantanes,
        resultat.temps_instantanes,
    ):
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

    figure.suptitle(
        f"Transport par le vent : ({resultat.vitesse_x:.1f}, "
        f"{resultat.vitesse_y:.1f}) km/h",
        fontsize=14,
    )
    figure.tight_layout()
    figure.savefig(sortie / "transport_instants.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def enregistrer_comparaison(
    resultats: list[ResultatSimulation],
    longueur: float,
    sortie: Path,
) -> None:
    """Compare les concentrations finales de trois scénarios de vent."""

    maximum = max(float(np.max(r.instantanes[-1])) for r in resultats)
    figure, axes = plt.subplots(1, len(resultats), figsize=(15, 4.8))

    for axe, resultat in zip(axes, resultats):
        affichage = axe.imshow(
            resultat.instantanes[-1],
            origin="lower",
            extent=[0.0, longueur, 0.0, longueur],
            cmap="inferno",
            vmin=0.0,
            vmax=maximum,
        )
        axe.plot(resultat.centres_x[-1], resultat.centres_y[-1], "co", ms=6)
        axe.set_title(resultat.nom)
        axe.set_xlabel("x (km)")
        axe.set_ylabel("y (km)")
        figure.colorbar(affichage, ax=axe, fraction=0.046, pad=0.04)

    figure.suptitle("Effet de la direction du vent sur le polluant", fontsize=14)
    figure.tight_layout()
    figure.savefig(
        sortie / "comparaison_scenarios.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


def enregistrer_trajectoires(
    resultats: list[ResultatSimulation],
    sortie: Path,
) -> None:
    """Trace le déplacement du centre du nuage pour chaque scénario."""

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for resultat in resultats:
        axes[0].plot(resultat.temps, resultat.centres_x, label=resultat.nom)
        axes[1].plot(resultat.temps, resultat.centres_y, label=resultat.nom)

    axes[0].set_title("Déplacement est-ouest")
    axes[0].set_ylabel("Centre x (km)")
    axes[1].set_title("Déplacement nord-sud")
    axes[1].set_ylabel("Centre y (km)")
    for axe in axes:
        axe.set_xlabel("Temps (h)")
        axe.grid(alpha=0.3)
        axe.legend()

    figure.tight_layout()
    figure.savefig(
        sortie / "trajectoires_centres.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


def enregistrer_animation(
    resultat: ResultatSimulation,
    duree: float,
    longueur: float,
    sortie: Path,
) -> None:
    """Crée un GIF du scénario principal."""

    figure, axe = plt.subplots(figsize=(6.5, 5.5))
    maximum = float(np.max(resultat.images_animation[0]))
    affichage = axe.imshow(
        resultat.images_animation[0],
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
        affichage.set_data(resultat.images_animation[numero])
        temps = duree * numero / max(1, len(resultat.images_animation) - 1)
        titre.set_text(f"t = {temps:.2f} h")
        return affichage, titre

    film = animation.FuncAnimation(
        figure,
        mettre_a_jour,
        frames=len(resultat.images_animation),
        interval=80,
        blit=False,
    )
    film.save(sortie / "transport_vent.gif", writer="pillow", fps=12)
    plt.close(figure)


def enregistrer_diagnostics(
    resultats: list[ResultatSimulation],
    sortie: Path,
) -> None:
    """Enregistre les indicateurs permettant d'interpréter les résultats."""

    with (sortie / "diagnostics.csv").open("w", newline="", encoding="utf-8") as fichier:
        redacteur = csv.writer(fichier)
        redacteur.writerow(
            ["scenario", "temps_h", "masse", "minimum", "centre_x_km", "centre_y_km"]
        )
        for resultat in resultats:
            for ligne in zip(
                resultat.temps,
                resultat.masses,
                resultat.minimums,
                resultat.centres_x,
                resultat.centres_y,
            ):
                redacteur.writerow([resultat.nom, *ligne])

    lignes = [
        "Bilan de l'étape 2 — transport par le vent",
        "",
        "Équation : dc/dt + u dc/dx + v dc/dy = D Delta(c)",
        "Schéma : Euler explicite + amont pour l'advection + différences centrées",
        "",
    ]
    for resultat in resultats:
        erreur_masse = abs(resultat.masses[-1] - resultat.masses[0]) / resultat.masses[0]
        lignes.extend(
            [
                resultat.nom,
                f"  vent : ({resultat.vitesse_x:.6f}, {resultat.vitesse_y:.6f}) km/h",
                f"  centre initial : ({resultat.centres_x[0]:.6f}, {resultat.centres_y[0]:.6f}) km",
                f"  centre final : ({resultat.centres_x[-1]:.6f}, {resultat.centres_y[-1]:.6f}) km",
                f"  minimum final : {resultat.minimums[-1]:.12e}",
                f"  variation relative de masse : {erreur_masse:.12e}",
                "",
            ]
        )

    (sortie / "bilan.txt").write_text("\n".join(lignes), encoding="utf-8")


def main() -> None:
    """Lance trois scénarios et produit les comparaisons."""

    arguments = lire_arguments()
    verifier_arguments(arguments)
    arguments.sortie.mkdir(parents=True, exist_ok=True)

    pas_espace = arguments.longueur / (arguments.taille - 1)
    axe = np.linspace(0.0, arguments.longueur, arguments.taille)
    x, y = np.meshgrid(axe, axe)
    depart = concentration_initiale(x, y, arguments.longueur)
    depart /= masse_totale(depart, pas_espace)

    configurations = [
        ("Sans vent", 0.0, 0.0),
        ("Vent vers l'est", arguments.vent_x, 0.0),
        ("Vent oblique", arguments.vent_x, arguments.vent_y),
    ]
    resultats = [
        simuler_scenario(
            nom,
            depart,
            x,
            y,
            pas_espace,
            arguments.duree,
            arguments.diffusion,
            vitesse_x,
            vitesse_y,
            arguments.securite,
        )
        for nom, vitesse_x, vitesse_y in configurations
    ]

    scenario_principal = resultats[-1]
    enregistrer_instantanes(scenario_principal, arguments.longueur, arguments.sortie)
    enregistrer_comparaison(resultats, arguments.longueur, arguments.sortie)
    enregistrer_trajectoires(resultats, arguments.sortie)
    enregistrer_animation(
        scenario_principal,
        arguments.duree,
        arguments.longueur,
        arguments.sortie,
    )
    enregistrer_diagnostics(resultats, arguments.sortie)

    print(f"Natayij t7ettou f: {arguments.sortie.resolve()}")
    print(
        "Markaz dyal nuage f nihaya: "
        f"({scenario_principal.centres_x[-1]:.3f}, "
        f"{scenario_principal.centres_y[-1]:.3f}) km"
    )
    print(f"A9al tarkiz: {min(scenario_principal.minimums):.6e}")


if __name__ == "__main__":
    main()
