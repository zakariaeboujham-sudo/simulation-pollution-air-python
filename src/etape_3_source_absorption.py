"""Etape 3 : emission continue et zone absorbante.

Le programme resout en deux dimensions l'equation

    dc/dt + div(v c) = D Delta(c) + S(x, y, t) - k(x, y) c.

Le transport est discretise sous forme conservative par un schema amont.
La diffusion utilise un laplacien a cinq points et le temps un schema
d'Euler explicite. Deux scenarios strictement comparables sont simules :
sans absorption, puis avec une ceinture vegetale absorbante.
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
from matplotlib.patches import Rectangle


@dataclass
class ResultatSimulation:
    """Diagnostics et champs produits pour un scenario."""

    nom: str
    temps: list[float]
    masses: list[float]
    emissions_cumulees: list[float]
    absorptions_cumulees: list[float]
    concentrations_urbaines: list[float]
    expositions_urbaines: list[float]
    maximums: list[float]
    minimums: list[float]
    erreurs_bilan: list[float]
    instantanes: list[np.ndarray]
    temps_instantanes: list[float]
    images_animation: list[np.ndarray]
    temps_animation: list[float]
    concentration_finale: np.ndarray
    pas_temps: float
    nombre_etapes: int


def lire_arguments() -> argparse.Namespace:
    """Lit les parametres de l'experience numerique."""

    analyseur = argparse.ArgumentParser(
        description="Comparer une dispersion avec et sans zone absorbante."
    )
    analyseur.add_argument("--taille", type=int, default=121)
    analyseur.add_argument("--longueur", type=float, default=100.0)
    analyseur.add_argument("--duree", type=float, default=24.0)
    analyseur.add_argument("--diffusion", type=float, default=1.5)
    analyseur.add_argument("--vent-x", type=float, default=3.0)
    analyseur.add_argument("--vent-y", type=float, default=0.3)
    analyseur.add_argument(
        "--emission",
        type=float,
        default=1.0,
        help="Masse emise par heure tant que la source est active.",
    )
    analyseur.add_argument(
        "--duree-emission",
        type=float,
        default=18.0,
        help="Duree de fonctionnement de la source, en heures.",
    )
    analyseur.add_argument(
        "--absorption",
        type=float,
        default=0.45,
        help="Taux maximal d'absorption de la ceinture, en h^-1.",
    )
    analyseur.add_argument("--securite", type=float, default=0.85)
    analyseur.add_argument(
        "--sans-animation",
        action="store_true",
        help="Ne pas produire le GIF (execution plus rapide).",
    )
    analyseur.add_argument(
        "--sortie",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "resultats" / "etape_3",
    )
    return analyseur.parse_args()


def verifier_arguments(arguments: argparse.Namespace) -> None:
    """Refuse les configurations qui ne definissent pas une experience valide."""

    for nom in ("longueur", "duree", "diffusion", "vent_x", "vent_y",
                "emission", "duree_emission", "absorption", "securite"):
        if not math.isfinite(getattr(arguments, nom)):
            raise ValueError(f"Le parametre {nom} doit etre fini.")
    if arguments.taille < 31:
        raise ValueError("La grille doit contenir au moins 31 points par axe.")
    if arguments.longueur <= 0.0 or arguments.duree <= 0.0:
        raise ValueError("La longueur et la duree doivent etre positives.")
    if arguments.diffusion < 0.0:
        raise ValueError("Le coefficient de diffusion ne peut pas etre negatif.")
    if arguments.emission <= 0.0 or arguments.duree_emission <= 0.0:
        raise ValueError("L'emission et sa duree doivent etre positives.")
    if arguments.absorption <= 0.0:
        raise ValueError("Le taux d'absorption doit etre positif.")
    if not 0.0 < arguments.securite <= 1.0:
        raise ValueError("Le facteur de securite doit appartenir a ]0, 1].")


def masse_totale(concentration: np.ndarray, pas_espace: float) -> float:
    """Approche l'integrale de la concentration sur le domaine."""

    return float(np.sum(concentration) * pas_espace**2)


def forme_source(
    x: np.ndarray,
    y: np.ndarray,
    longueur: float,
    pas_espace: float,
) -> np.ndarray:
    """Construit une source gaussienne d'integrale discrete egale a un."""

    centre_x = 0.15 * longueur
    centre_y = 0.50 * longueur
    largeur = 0.025 * longueur
    source = np.exp(
        -((x - centre_x) ** 2 + (y - centre_y) ** 2) / (2.0 * largeur**2)
    )
    return source / masse_totale(source, pas_espace)


def masque_ceinture(
    x: np.ndarray,
    y: np.ndarray,
    longueur: float,
) -> np.ndarray:
    """Represente une ceinture vegetale verticale placee avant la ville."""

    return (
        (x >= 0.53 * longueur)
        & (x <= 0.60 * longueur)
        & (y >= 0.22 * longueur)
        & (y <= 0.78 * longueur)
    )


def masque_zone_urbaine(
    x: np.ndarray,
    y: np.ndarray,
    longueur: float,
) -> np.ndarray:
    """Definit la zone dans laquelle l'exposition est mesuree."""

    return (
        (x >= 0.72 * longueur)
        & (x <= 0.92 * longueur)
        & (y >= 0.30 * longueur)
        & (y <= 0.70 * longueur)
    )


def laplacien_sans_flux(
    concentration: np.ndarray,
    pas_espace: float,
) -> np.ndarray:
    """Calcule le laplacien avec une derivee normale nulle aux bords."""

    prolongee = np.pad(concentration, 1, mode="edge")
    voisins = (
        prolongee[2:, 1:-1]
        + prolongee[:-2, 1:-1]
        + prolongee[1:-1, 2:]
        + prolongee[1:-1, :-2]
    )
    return (voisins - 4.0 * concentration) / pas_espace**2


def divergence_advection_sans_flux(
    concentration: np.ndarray,
    pas_espace: float,
    vitesse_x: float,
    vitesse_y: float,
) -> np.ndarray:
    """Calcule div(v*c) par flux amont conservatifs et flux nul aux bords."""

    ny, nx = concentration.shape
    flux_x = np.zeros((ny, nx + 1), dtype=float)
    flux_y = np.zeros((ny + 1, nx), dtype=float)

    if vitesse_x >= 0.0:
        flux_x[:, 1:-1] = vitesse_x * concentration[:, :-1]
    else:
        flux_x[:, 1:-1] = vitesse_x * concentration[:, 1:]

    if vitesse_y >= 0.0:
        flux_y[1:-1, :] = vitesse_y * concentration[:-1, :]
    else:
        flux_y[1:-1, :] = vitesse_y * concentration[1:, :]

    return (flux_x[:, 1:] - flux_x[:, :-1]) / pas_espace + (
        flux_y[1:, :] - flux_y[:-1, :]
    ) / pas_espace


def calculer_pas_temps(
    pas_espace: float,
    diffusion: float,
    vitesse_x: float,
    vitesse_y: float,
    absorption_maximale: float,
    securite: float,
) -> float:
    """Impose la condition CFL combinee de l'operateur explicite."""

    taux = (
        (abs(vitesse_x) + abs(vitesse_y)) / pas_espace
        + 4.0 * diffusion / pas_espace**2
        + absorption_maximale
    )
    if taux <= 0.0:
        raise ValueError("Au moins un mecanisme d'evolution doit etre actif.")
    return securite / taux


def concentration_moyenne_zone(
    concentration: np.ndarray,
    masque: np.ndarray,
) -> float:
    """Retourne la concentration moyenne sur les mailles de la zone urbaine."""

    return float(np.mean(concentration[masque]))


def indices_instantanes(nombre_etapes: int) -> list[int]:
    """Selectionne quatre instants representatifs."""

    return sorted(
        {0, nombre_etapes // 3, 2 * nombre_etapes // 3, nombre_etapes}
    )


def simuler_scenario(
    nom: str,
    source_unitaire: np.ndarray,
    masque_urbain: np.ndarray,
    taux_absorption: np.ndarray,
    pas_espace: float,
    duree: float,
    duree_emission: float,
    intensite_emission: float,
    diffusion: float,
    vitesse_x: float,
    vitesse_y: float,
    securite: float,
    absorption_cfl: float | None = None,
) -> ResultatSimulation:
    """Integre l'equation source-advection-diffusion-absorption."""

    pas_maximal = calculer_pas_temps(
        pas_espace,
        diffusion,
        vitesse_x,
        vitesse_y,
        max(float(np.max(taux_absorption)), absorption_cfl or 0.0),
        securite,
    )
    nombre_etapes = math.ceil(duree / pas_maximal)
    pas_temps = duree / nombre_etapes
    choix_instantanes = set(indices_instantanes(nombre_etapes))
    frequence_animation = max(1, nombre_etapes // 100)

    concentration = np.zeros_like(source_unitaire)
    temps = [0.0]
    masses = [0.0]
    emissions_cumulees = [0.0]
    absorptions_cumulees = [0.0]
    concentrations_urbaines = [0.0]
    expositions_urbaines = [0.0]
    maximums = [0.0]
    minimums = [0.0]
    erreurs_bilan = [0.0]
    instantanes = [concentration.copy()]
    temps_instantanes = [0.0]
    images_animation = [concentration.copy()]
    temps_animation = [0.0]

    for etape in range(1, nombre_etapes + 1):
        temps_precedent = (etape - 1) * pas_temps
        fraction_source = float(
            np.clip((duree_emission - temps_precedent) / pas_temps, 0.0, 1.0)
        )
        source = intensite_emission * fraction_source * source_unitaire
        absorption_locale = taux_absorption * concentration
        divergence = divergence_advection_sans_flux(
            concentration,
            pas_espace,
            vitesse_x,
            vitesse_y,
        )
        concentration_nouvelle = concentration + pas_temps * (
            diffusion * laplacien_sans_flux(concentration, pas_espace)
            - divergence
            + source
            - absorption_locale
        )
        # Ne pas masquer une instabilite par un ecretage des concentrations.
        if not np.all(np.isfinite(concentration_nouvelle)):
            raise FloatingPointError("Concentration non finie.")
        tolerance = 1e-12 * max(1.0, float(np.max(concentration_nouvelle)))
        if float(np.min(concentration_nouvelle)) < -tolerance:
            raise FloatingPointError("Positivite violee : verifier le pas de temps.")

        emission_incrementale = (
            intensite_emission * fraction_source * pas_temps
        )
        absorption_incrementale = (
            masse_totale(absorption_locale, pas_espace) * pas_temps
        )
        emission_totale = emissions_cumulees[-1] + emission_incrementale
        absorption_totale = absorptions_cumulees[-1] + absorption_incrementale
        masse = masse_totale(concentration_nouvelle, pas_espace)
        temps_actuel = etape * pas_temps
        concentration_urbaine = concentration_moyenne_zone(
            concentration_nouvelle,
            masque_urbain,
        )
        exposition = expositions_urbaines[-1] + 0.5 * pas_temps * (
            concentrations_urbaines[-1] + concentration_urbaine
        )
        erreur_bilan = masse - (emission_totale - absorption_totale)

        concentration = concentration_nouvelle
        temps.append(temps_actuel)
        masses.append(masse)
        emissions_cumulees.append(emission_totale)
        absorptions_cumulees.append(absorption_totale)
        concentrations_urbaines.append(concentration_urbaine)
        expositions_urbaines.append(exposition)
        maximums.append(float(np.max(concentration)))
        minimums.append(float(np.min(concentration)))
        erreurs_bilan.append(erreur_bilan)

        if etape in choix_instantanes:
            instantanes.append(concentration.copy())
            temps_instantanes.append(temps_actuel)
        if etape % frequence_animation == 0 or etape == nombre_etapes:
            images_animation.append(concentration.copy())
            temps_animation.append(temps_actuel)

    return ResultatSimulation(
        nom=nom,
        temps=temps,
        masses=masses,
        emissions_cumulees=emissions_cumulees,
        absorptions_cumulees=absorptions_cumulees,
        concentrations_urbaines=concentrations_urbaines,
        expositions_urbaines=expositions_urbaines,
        maximums=maximums,
        minimums=minimums,
        erreurs_bilan=erreurs_bilan,
        instantanes=instantanes,
        temps_instantanes=temps_instantanes,
        images_animation=images_animation,
        temps_animation=temps_animation,
        concentration_finale=concentration.copy(),
        pas_temps=pas_temps,
        nombre_etapes=nombre_etapes,
    )


def ajouter_reperes(
    axe: plt.Axes,
    longueur: float,
    afficher_ceinture: bool,
) -> None:
    """Ajoute source, ville et ceinture aux cartes de concentration."""

    axe.plot(0.15 * longueur, 0.50 * longueur, "wo", ms=5, mec="black")
    axe.add_patch(
        Rectangle(
            (0.72 * longueur, 0.30 * longueur),
            0.20 * longueur,
            0.40 * longueur,
            fill=False,
            edgecolor="cyan",
            linewidth=1.8,
            label="Zone urbaine",
        )
    )
    if afficher_ceinture:
        axe.add_patch(
            Rectangle(
                (0.53 * longueur, 0.22 * longueur),
                0.07 * longueur,
                0.56 * longueur,
                facecolor="lime",
                edgecolor="lime",
                alpha=0.22,
                linewidth=1.5,
                label="Ceinture absorbante",
            )
        )


def enregistrer_instantanes(
    resultat: ResultatSimulation,
    longueur: float,
    sortie: Path,
) -> None:
    """Enregistre quatre cartes temporelles du scenario avec ceinture."""

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
        ajouter_reperes(axe, longueur, afficher_ceinture=True)
        axe.set_title(f"t = {temps:.2f} h")
        axe.set_xlabel("x (km)")
        axe.set_ylabel("y (km)")
        figure.colorbar(affichage, ax=axe, fraction=0.046, pad=0.04)
    figure.suptitle("Source temporaire et ceinture absorbante", fontsize=14)
    figure.tight_layout()
    figure.savefig(sortie / "evolution_avec_ceinture.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def enregistrer_comparaison(
    sans_absorption: ResultatSimulation,
    avec_absorption: ResultatSimulation,
    longueur: float,
    sortie: Path,
) -> None:
    """Compare les champs finaux et la concentration evitee."""

    maximum = max(
        float(np.max(sans_absorption.concentration_finale)),
        float(np.max(avec_absorption.concentration_finale)),
    )
    difference = (
        sans_absorption.concentration_finale - avec_absorption.concentration_finale
    )
    figure, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    for axe, resultat, ceinture in zip(
        axes[:2],
        [sans_absorption, avec_absorption],
        [False, True],
    ):
        affichage = axe.imshow(
            resultat.concentration_finale,
            origin="lower",
            extent=[0.0, longueur, 0.0, longueur],
            cmap="inferno",
            vmin=0.0,
            vmax=maximum,
        )
        ajouter_reperes(axe, longueur, ceinture)
        axe.set_title(resultat.nom)
        axe.set_xlabel("x (km)")
        axe.set_ylabel("y (km)")
        figure.colorbar(affichage, ax=axe, fraction=0.046, pad=0.04)

    limite = max(abs(float(np.min(difference))), abs(float(np.max(difference))))
    affichage_difference = axes[2].imshow(
        difference,
        origin="lower",
        extent=[0.0, longueur, 0.0, longueur],
        cmap="coolwarm",
        vmin=-limite,
        vmax=limite,
    )
    ajouter_reperes(axes[2], longueur, afficher_ceinture=True)
    axes[2].set_title("Concentration evitee")
    axes[2].set_xlabel("x (km)")
    axes[2].set_ylabel("y (km)")
    figure.colorbar(affichage_difference, ax=axes[2], fraction=0.046, pad=0.04)
    figure.suptitle("Effet final de la zone absorbante", fontsize=14)
    figure.tight_layout()
    figure.savefig(sortie / "comparaison_finale.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def enregistrer_exposition(
    resultats: list[ResultatSimulation],
    sortie: Path,
) -> None:
    """Trace la concentration et l'exposition cumulee dans la ville."""

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for resultat in resultats:
        axes[0].plot(
            resultat.temps,
            resultat.concentrations_urbaines,
            label=resultat.nom,
        )
        axes[1].plot(
            resultat.temps,
            resultat.expositions_urbaines,
            label=resultat.nom,
        )
    axes[0].set_title("Concentration moyenne dans la ville")
    axes[0].set_ylabel("Concentration moyenne")
    axes[1].set_title("Exposition urbaine cumulee")
    axes[1].set_ylabel("Concentration x heure")
    for axe in axes:
        axe.set_xlabel("Temps (h)")
        axe.grid(alpha=0.3)
        axe.legend()
    figure.tight_layout()
    figure.savefig(sortie / "exposition_urbaine.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def enregistrer_bilan_masse(
    resultat: ResultatSimulation,
    sortie: Path,
) -> None:
    """Visualise le bilan emission - absorption - masse restante."""

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(resultat.temps, resultat.emissions_cumulees, label="Emise")
    axes[0].plot(resultat.temps, resultat.absorptions_cumulees, label="Absorbee")
    axes[0].plot(resultat.temps, resultat.masses, label="Dans le domaine")
    axes[0].set_title("Bilan de masse avec ceinture")
    axes[0].set_xlabel("Temps (h)")
    axes[0].set_ylabel("Masse")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(resultat.temps, resultat.erreurs_bilan)
    axes[1].set_title("Residus du bilan numerique")
    axes[1].set_xlabel("Temps (h)")
    axes[1].set_ylabel("Masse calculee - masse attendue")
    axes[1].grid(alpha=0.3)
    figure.tight_layout()
    figure.savefig(sortie / "bilan_masse.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def enregistrer_animation(
    resultat: ResultatSimulation,
    duree: float,
    longueur: float,
    sortie: Path,
) -> None:
    """Cree un GIF du scenario avec zone absorbante."""

    figure, axe = plt.subplots(figsize=(6.6, 5.6))
    maximum = max(float(np.max(image)) for image in resultat.images_animation)
    affichage = axe.imshow(
        resultat.images_animation[0],
        origin="lower",
        extent=[0.0, longueur, 0.0, longueur],
        cmap="inferno",
        vmin=0.0,
        vmax=maximum,
    )
    ajouter_reperes(axe, longueur, afficher_ceinture=True)
    titre = axe.set_title("t = 0.00 h")
    axe.set_xlabel("x (km)")
    axe.set_ylabel("y (km)")
    figure.colorbar(affichage, ax=axe, label="Concentration")

    def mettre_a_jour(numero: int) -> tuple[object, object]:
        affichage.set_data(resultat.images_animation[numero])
        temps = resultat.temps_animation[numero]
        titre.set_text(f"t = {temps:.2f} h")
        return affichage, titre

    film = animation.FuncAnimation(
        figure,
        mettre_a_jour,
        frames=len(resultat.images_animation),
        interval=80,
        blit=False,
    )
    film.save(sortie / "source_et_ceinture.gif", writer="pillow", fps=12)
    plt.close(figure)


def enregistrer_diagnostics(
    resultats: list[ResultatSimulation],
    sortie: Path,
) -> None:
    """Ecrit les series temporelles et un bilan lisible."""

    with (sortie / "diagnostics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fichier:
        redacteur = csv.writer(fichier)
        redacteur.writerow(
            [
                "scenario",
                "temps_h",
                "masse",
                "emission_cumulee",
                "absorption_cumulee",
                "concentration_urbaine",
                "exposition_urbaine",
                "minimum",
                "maximum",
                "erreur_bilan",
            ]
        )
        for resultat in resultats:
            for ligne in zip(
                resultat.temps,
                resultat.masses,
                resultat.emissions_cumulees,
                resultat.absorptions_cumulees,
                resultat.concentrations_urbaines,
                resultat.expositions_urbaines,
                resultat.minimums,
                resultat.maximums,
                resultat.erreurs_bilan,
            ):
                redacteur.writerow([resultat.nom, *ligne])

    sans_absorption, avec_absorption = resultats
    exposition_reference = sans_absorption.expositions_urbaines[-1]
    exposition_ceinture = avec_absorption.expositions_urbaines[-1]
    reduction = (
        100.0 * (1.0 - exposition_ceinture / exposition_reference)
        if exposition_reference > 0.0 else float("nan")
    )
    fraction_absorbee = 100.0 * (
        avec_absorption.absorptions_cumulees[-1]
        / avec_absorption.emissions_cumulees[-1]
    )
    lignes = [
        "Bilan de l'etape 3 — source et zone absorbante",
        "",
        "Equation : dc/dt + div(v c) = D Delta(c) + S - k c",
        "Schema : volumes finis amont + diffusion centree + Euler explicite",
        f"Pas de temps : {avec_absorption.pas_temps:.8f} h",
        f"Nombre d'etapes : {avec_absorption.nombre_etapes}",
        f"Masse emise : {avec_absorption.emissions_cumulees[-1]:.8f}",
        f"Masse absorbee : {avec_absorption.absorptions_cumulees[-1]:.8f}",
        f"Fraction de la masse emise absorbee : {fraction_absorbee:.3f} %",
        f"Exposition urbaine sans ceinture : {exposition_reference:.8e}",
        f"Exposition urbaine avec ceinture : {exposition_ceinture:.8e}",
        f"Reduction de l'exposition urbaine : {reduction:.3f} %",
        (
            "Erreur maximale du bilan de masse : "
            f"{max(abs(e) for e in avec_absorption.erreurs_bilan):.12e}"
        ),
        f"Concentration minimale : {min(avec_absorption.minimums):.12e}",
    ]
    (sortie / "bilan.txt").write_text("\n".join(lignes), encoding="utf-8")


def main() -> None:
    """Lance les deux scenarios et produit les comparaisons."""

    arguments = lire_arguments()
    verifier_arguments(arguments)
    arguments.sortie.mkdir(parents=True, exist_ok=True)

    # Mailles centrees : N cellules couvrent exactement [0, longueur].
    pas_espace = arguments.longueur / arguments.taille
    axe = (np.arange(arguments.taille) + 0.5) * pas_espace
    x, y = np.meshgrid(axe, axe)
    source_unitaire = forme_source(x, y, arguments.longueur, pas_espace)
    masque_urbain = masque_zone_urbaine(x, y, arguments.longueur)
    ceinture = masque_ceinture(x, y, arguments.longueur)

    configurations = [
        ("Sans ceinture absorbante", np.zeros_like(x)),
        (
            "Avec ceinture absorbante",
            arguments.absorption * ceinture.astype(float),
        ),
    ]
    resultats = [
        simuler_scenario(
            nom=nom,
            source_unitaire=source_unitaire,
            masque_urbain=masque_urbain,
            taux_absorption=taux_absorption,
            pas_espace=pas_espace,
            duree=arguments.duree,
            duree_emission=arguments.duree_emission,
            intensite_emission=arguments.emission,
            diffusion=arguments.diffusion,
            vitesse_x=arguments.vent_x,
            vitesse_y=arguments.vent_y,
            securite=arguments.securite,
            absorption_cfl=arguments.absorption,
        )
        for nom, taux_absorption in configurations
    ]

    sans_absorption, avec_absorption = resultats
    enregistrer_instantanes(avec_absorption, arguments.longueur, arguments.sortie)
    enregistrer_comparaison(
        sans_absorption,
        avec_absorption,
        arguments.longueur,
        arguments.sortie,
    )
    enregistrer_exposition(resultats, arguments.sortie)
    enregistrer_bilan_masse(avec_absorption, arguments.sortie)
    if not arguments.sans_animation:
        enregistrer_animation(
            avec_absorption,
            arguments.duree,
            arguments.longueur,
            arguments.sortie,
        )
    enregistrer_diagnostics(resultats, arguments.sortie)

    exposition_reference = sans_absorption.expositions_urbaines[-1]
    reduction = 100.0 * (
        1.0 - avec_absorption.expositions_urbaines[-1] / exposition_reference
    ) if exposition_reference > 0.0 else float("nan")
    print(f"Resultats enregistres dans : {arguments.sortie.resolve()}")
    print(f"Reduction de l'exposition urbaine : {reduction:.2f} %")
    print(
        "Erreur maximale du bilan de masse : "
        f"{max(abs(e) for e in avec_absorption.erreurs_bilan):.3e}"
    )


if __name__ == "__main__":
    main()
