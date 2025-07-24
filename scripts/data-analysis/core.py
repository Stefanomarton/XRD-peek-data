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


def create_peak_table_csv(directory, outdir=None):
    """
    Generate peak table CSV from .REF and peak_*.xy files.
    """
    import os
    outdir = outdir or directory
    os.makedirs(outdir, exist_ok=True)

    ref_path = next((os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".REF")), None)
    peak_count = len([f for f in os.listdir(directory) if f.startswith("peak_") and f.endswith(".xy")])
    name = os.path.basename(directory.rstrip("/"))

    if not ref_path or not peak_count:
        return None  # nothing to do

    csv_path = os.path.join(outdir, f"{name}_peak_table.csv")
    save_peak_table_csv(directory, ref_path, peak_count, outdir)

    return csv_path

# ------------------------------------------------------------------
# Per-sample plot (peaks + calc + experimental + residuals)
# ------------------------------------------------------------------
def plot_from_directory(
    directory,
    outdir=None,
    show_residuals=True,
):
    """
    Plot one sample folder: peak_x.xy components, wpl_fit.cal (sum),
    experimental G*.xy or G*.dat, residuals.
    """

    peak_paths = sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith("peak_") and f.endswith(".xy")
    )
    calc_sum_path = next(
        (os.path.join(directory, f) for f in os.listdir(directory) if f.endswith("wpl_fit.cal")), None
    )
    experimental_path = next(
        (os.path.join(directory, f) for f in os.listdir(directory)
         if f.startswith("G") and (f.endswith(".xy") or f.endswith(".dat"))),
        None
    )

    if not peak_paths or calc_sum_path is None or experimental_path is None:
        raise FileNotFoundError(f"Missing required files in {directory}")

    peak_data = [load_xy(p) for p in peak_paths]
    all_x = np.concatenate([d[:, 0] for d in peak_data])
    x_common = np.linspace(all_x.min(), all_x.max(), 4000)
    y_total = np.zeros_like(x_common)

    if show_residuals:
        fig, axes = plt.subplots(nrows=2, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        ax1, ax2 = axes
    else:
        fig, ax1 = plt.subplots(figsize=(10, 4))
        ax2 = None

    for pth, data in zip(peak_paths, peak_data):
        x_peak, y_peak = data[:, 0], data[:, 1]
        y_interp = np.interp(x_common, x_peak, y_peak)
        y_total += y_interp
        ax1.plot(x_peak, y_peak, '--', label=os.path.basename(pth).replace('.xy', ''))

    x_calc, y_calc = load_xy(calc_sum_path).T
    ax1.plot(x_calc, y_calc, 'k-', linewidth=1.2, label='Calculated')

    x_exp, y_exp = load_xy(experimental_path).T
    ax1.plot(x_exp, y_exp, 'r-', alpha=0.5, label='Experimental')

    name = os.path.basename(directory.rstrip("/"))
    ax1.set_ylabel('Intensity (a.u.)')
    ax1.set_title(f'{name} — Peak Fit')
    ax1.legend(fontsize='small')
    ax1.grid(False)

    if show_residuals and ax2 is not None:
        xmin, xmax = x_calc.min(), x_calc.max()
        mask = (x_exp >= xmin) & (x_exp <= xmax)
        x_exp_in = x_exp[mask]
        y_exp_in = y_exp[mask]
        y_calc_interp = np.interp(x_exp_in, x_calc, y_calc)
        residuals = y_exp_in - y_calc_interp

        ax2.plot(x_exp_in, residuals, 'b-', label='Residuals')
        ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax2.set_ylim(-20, 20)
        ax2.set_xlabel('2θ (degrees)')
        ax2.set_ylabel('Residuals')
        ax2.set_title(f'Residuals: {xmin:.2f}°– {xmax:.2f}°')
        ax2.grid(False)
        ax2.legend()
    else:
        ax1.set_xlabel('2θ (degrees)')

    plt.subplots_adjust(bottom=0.1)

    outdir = outdir or directory
    os.makedirs(outdir, exist_ok=True)

    pdf_path = os.path.join(outdir, f"{name}_fit_plot.png")
    plt.savefig(pdf_path, bbox_inches="tight", dpi=500)
    print(f"Saved plot: {pdf_path}")

    plt.close(fig)
