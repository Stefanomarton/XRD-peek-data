import os
import re
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib import cm

# ------------------------------------------------------------------
# Data loading utilities
# ------------------------------------------------------------------
def load_xy(filepath):
    """Load 2-column text data (2θ, Intensity), skipping comment lines."""
    with open(filepath, "r") as f:
        lines = [ln for ln in f if not ln.strip().startswith(("!", "#")) and ln.strip()]
    return np.loadtxt(StringIO("".join(lines)))


_num_pat = re.compile(r"[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?")


def _tokenize_numbers(line):
    return _num_pat.findall(line)


# ------------------------------------------------------------------
# .REF parsing
# ------------------------------------------------------------------
def extract_peaks_from_ref(ref_path, n):
    """
    Extract last n peak rows from a WinPLOTR .REF file.

    Returns 5 lists (length ≤ n if malformed rows are skipped):
        positions, intensities, sigmas_I, fwhms, sigmas_FWHM
    Missing FWHM columns → NaN placeholders.
    """
    with open(ref_path, "r") as f:
        lines = f.readlines()

    # Select only lines that begin with a float (peak rows)
    data_lines = [ln for ln in lines if re.match(r"^\s*\d+\.\d+", ln)]
    selected = data_lines[-n:] if n <= len(data_lines) else data_lines

    positions, intensities, sigmas_I, fwhms, sigmas_F = [], [], [], [], []
    for ln in selected:
        toks = _tokenize_numbers(ln)
        # Need at least Position, _, Intensity, Sigma_I
        if len(toks) < 4:
            continue
        try:
            positions.append(float(toks[0]))
            intensities.append(float(toks[2]))
            sigmas_I.append(float(toks[3]))
            if len(toks) >= 6:
                fwhms.append(float(toks[4]))
                sigmas_F.append(float(toks[5]))
            else:
                fwhms.append(np.nan)
                sigmas_F.append(np.nan)
        except ValueError:
            # Skip malformed row
            continue

    return positions, intensities, sigmas_I, fwhms, sigmas_F


# ------------------------------------------------------------------
# Peak table CSV export
# ------------------------------------------------------------------
def save_peak_table_csv(directory, ref_path, n, outdir=None):
    positions, intensities, sigmas, fwhms, fwhm_sigmas = extract_peaks_from_ref(ref_path, n)
    name = os.path.basename(directory.rstrip("/"))
    outdir = outdir or directory
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"{name}_peak_table.csv")

    with open(outpath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Position (°)", "Intensity", "Sigma", "FWHM", "FWHM Sigma"])
        for pos, inten, sigma, fw, fw_sigma in zip(positions, intensities, sigmas, fwhms, fwhm_sigmas):
            writer.writerow([
                f"{pos:.4f}",
                f"{inten:.2f}",
                f"{sigma:.2f}",
                "" if np.isnan(fw) else f"{fw:.4f}",
                "" if np.isnan(fw_sigma) else f"{fw_sigma:.4f}",
            ])

    print(f"Saved table CSV: {outpath}")
