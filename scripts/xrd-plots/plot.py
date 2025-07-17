#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# === PARAMETRI DA PERSONALIZZARE =========================================================
cartella_dati  = Path("../data")          # directory con i file .xy
x_min, x_max   = 5.0, 40.0                                # intervallo 2θ in °
offset_y       = 10                                     # distanza verticale (unità intensità)

# Dizionario: nome_output : [lista di file (ordine desiderato)]
overlay_groups = {
    "cristallino": [
        "G112--5-40-0.01-1000ms.xy",
        "G111--5-40-0.01-1000ms.xy",
        "G110--5-40-0.01-1000ms.xy",
        "G109--5-40-0.01-1000ms.xy",
        "G107--5-40-0.01-1000ms.xy",
        "G106--5-40-0.01-1000ms.xy",
        "G105--5-40-0.01-1000ms.xy",
        "G104--5-40-0.01-1000ms.xy",
        "G102--5-40-0.01-1000ms.xy",
        "G101--5-40-0.01-1000ms.xy",],
    
    "amorfo": [
    "G312--5-40-0.01-1000ms.xy",
    "G311--5-40-0.01-1000ms.xy",
    "G310--5-40-0.01-1000ms.xy",
    "G309--5-40-0.01-1000ms.xy",
    "G307--5-40-0.01-1000ms.xy",
    "G306--5-40-0.01-1000ms.xy",
    "G305--5-40-0.01-1000ms.xy",
    "G304--5-40-0.01-1000ms.xy",
    "G302--5-40-0.01-1000ms.xy",
    "G301--5-40-0.01-1000ms.xy",],

"confronto-piatto-1-posizione-1": [
    "G301--5-40-0.01-1000ms.xy",
    "G101--5-40-0.01-1000ms.xy"
],

"confronto-piatto-1-posizione-2": [
    "G302--5-40-0.01-1000ms.xy",
    "G102--5-40-0.01-1000ms.xy"
],

"confronto-piatto-1-posizione-4": [
    "G304--5-40-0.01-1000ms.xy",
    "G104--5-40-0.01-1000ms.xy"
],

"confronto-piatto-2-posizione-1": [
    "G305--5-40-0.01-1000ms.xy",
    "G105--5-40-0.01-1000ms.xy"
],

"confronto-piatto-2-posizione-2": [
    "G306--5-40-0.01-1000ms.xy",
    "G106--5-40-0.01-1000ms.xy"
],

"confronto-piatto-2-posizione-3": [
    "G307--5-40-0.01-1000ms.xy",
    "G107--5-40-0.01-1000ms.xy"
],

"confronto-piatto-3-posizione-1": [
    "G309--5-40-0.01-1000ms.xy",
    "G109--5-40-0.01-1000ms.xy"
],

"confronto-piatto-3-posizione-2": [
    "G310--5-40-0.01-1000ms.xy",
    "G110--5-40-0.01-1000ms.xy"
],

"confronto-piatto-3-posizione-3": [
    "G311--5-40-0.01-1000ms.xy",
    "G111--5-40-0.01-1000ms.xy"
],

"confronto-piatto-3-posizione-4": [
    "G312--5-40-0.01-1000ms.xy",
    "G112--5-40-0.01-1000ms.xy"
],

"confronto-piatto-3-cristallino": [
    "G112--5-40-0.01-1000ms.xy",
    "G111--5-40-0.01-1000ms.xy",
    "G110--5-40-0.01-1000ms.xy",
    "G109--5-40-0.01-1000ms.xy",
],

"confronto-piatto-3-amorfo": [
    "G312--5-40-0.01-1000ms.xy",
    "G311--5-40-0.01-1000ms.xy",
    "G310--5-40-0.01-1000ms.xy",
    "G309--5-40-0.01-1000ms.xy",
],

}
# =========================================================================================

cartella_script = Path.cwd()
cartella_plots = Path("../plots")
cartella_plots.mkdir(exist_ok=True)

def leggi_xy(percorso: Path):
    """Ritorna due array numpy: 2θ (°) e intensità."""
    return np.loadtxt(percorso, comments="#", unpack=True)

def normalizza_nome(nome):
    return nome if nome.lower().endswith(".xy") else f"{nome}.xy"

# ------------- 1) individua tutti i file disponibili -------------------------------------
tutti_file = sorted(cartella_dati.glob("*.xy"))
if not tutti_file:
    raise FileNotFoundError(f"Nessun file .xy trovato in {cartella_dati}")

# ------------- 2) crea grafico sovrapposto di tutti i file -------------------------------
def plot_sovrapposto(file_paths, nome_out):
    """Crea un PNG sovrapposto dei file in file_paths, con offset verticale costante."""
    dati = []
    for p in file_paths:
        tt, ii = leggi_xy(p)
        mask   = (tt >= x_min) & (tt <= x_max)
        dati.append((tt[mask], ii[mask]))

    fig, ax = plt.subplots(figsize=(12, 8))
    for idx, (twotheta, intensita) in enumerate(dati):
        etichetta = file_paths[idx].stem.split('--')[0]   # "G312--5-40…" ➜ "G312"
        ax.plot(twotheta, intensita + idx * offset_y, label=etichetta)

    ax.set_xlabel(r"2θ (°)")
    ax.set_ylabel("Intensità (u. a.) + offset")
    ax.set_title(f"Pattern XRD – {nome_out}")

    # legenda sotto
    # plt.legend(fontsize="small", ncol=3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    fig.tight_layout()
    fig.savefig(cartella_plots / f"{nome_out}.png", dpi=300)
    plt.close(fig)

# sovrapposto di tutti
plot_sovrapposto(tutti_file, "sovrapposto_tutti")

def plot_sovrapposto_senza_offset(file_paths, nome_out):
    """Crea un PNG sovrapposto dei file in file_paths, con offset verticale costante."""
    dati = []
    for p in file_paths:
        tt, ii = leggi_xy(p)
        mask   = (tt >= x_min) & (tt <= x_max)
        dati.append((tt[mask], ii[mask]))

    fig, ax = plt.subplots(figsize=(12, 8))
    for idx, (twotheta, intensita) in enumerate(dati):
        etichetta = file_paths[idx].stem.split('--')[0]   # "G312--5-40…" ➜ "G312"
        ax.plot(twotheta, intensita, label=etichetta)

    ax.set_xlabel(r"2θ (°)")
    ax.set_ylabel("Intensità (u. a.) + offset")
    ax.set_title(f"Pattern XRD – {nome_out}")

    # legenda sotto
    # plt.legend(fontsize="small", ncol=3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    fig.tight_layout()
    fig.savefig(cartella_plots / f"{nome_out}.png", dpi=300)
    plt.close(fig)

# ------------- 3) grafici sovrapposti per ogni gruppo definito ---------------------------
for nome_gruppo, lista in overlay_groups.items():
    paths = [cartella_dati / normalizza_nome(n) for n in lista]
    mancanti = [p.name for p in paths if not p.is_file()]
    if mancanti:
        raise FileNotFoundError(f"Nel gruppo '{nome_gruppo}' mancano i file:\n  " +
                                "\n  ".join(mancanti))
    plot_sovrapposto_senza_offset(paths, f"sovrapposto_{nome_gruppo}")

# ------------- 4) PNG individuali (creati una sola volta) --------------------------------
for p in tutti_file:
    tt, ii = leggi_xy(p)
    mask   = (tt >= x_min) & (tt <= x_max)

    short_name = p.stem.split('--')[0]           # "G312--5-40…" ➜ "G312"
    
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tt[mask], ii[mask])
    ax.set_xlabel(r"2θ (°)")
    ax.set_ylabel("Intensità (u. a.)")
    ax.set_title(f"Pattern XRD – {short_name}")
    fig.tight_layout()
    fig.savefig(cartella_plots / f"{p.stem}.png", dpi=300)
    plt.close(fig)

print("Fatto! PNG salvati in:", cartella_plots.resolve())
