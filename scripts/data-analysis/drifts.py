import os
import re
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib import cm

# ------------------------------------------------------------------
# Peak position drift across samples
# ------------------------------------------------------------------
def plot_peak_position_drift(folder, save_path=None):
    """
    Line plot: peak index vs position across samples.
    """
    csv_files = sorted(f for f in os.listdir(folder) if f.endswith("_peak_table.csv"))
    if not csv_files:
        print(f"No peak_table CSVs found in {folder}.")
        return

    # Natural sort by numeric part
    csv_files.sort(key=lambda s: int(''.join(filter(str.isdigit, s)) or -1))
    sample_names = [f.replace("_peak_table.csv", "") for f in csv_files]

    # Build array (pad with NaN where peak missing)
    peak_lists = []
    max_peaks = 0
    for f in csv_files:
        df = pd.read_csv(os.path.join(folder, f))
        peak_lists.append(df["Position (°)"].to_numpy())
        max_peaks = max(max_peaks, len(df))

    arr = np.full((max_peaks, len(csv_files)), np.nan)
    for j, vals in enumerate(peak_lists):
        arr[:len(vals), j] = vals

    plt.figure(figsize=(14, 6))
    for i in range(max_peaks):
        plt.plot(sample_names, arr[i, :], marker='o', label=f"Peak {i+1}")

    plt.ylabel("Position (°)")
    plt.title("Peak Position Drift Across Samples")
    plt.xticks(rotation=45, ha="right")
    plt.grid(False)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.legend(title="Peak", bbox_to_anchor=(1.02, 1), loc='upper left')

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=500)
        print(f"Saved peak position drift plot to {save_path}")
        plt.close()
    else:
        plt.show()


# ------------------------------------------------------------------
# FWHM drift across samples
# ------------------------------------------------------------------
def plot_fwhm_drift_lines(folder, save_path=None, show_error=False):
    """
    Plot FWHM drift across samples.
        • folder      – directory that contains *_peak_table.csv files
        • save_path   – PDF/PNG path; if None, show interactively
        • show_error  – if True, add ±sigma error bars
    """
    csv_files = sorted(f for f in os.listdir(folder) if f.endswith("_peak_table.csv"))
    if not csv_files:
        print(f"No peak_table CSVs found in {folder}.")
        return

    # Natural sample order: G101, G102, ...
    csv_files.sort(key=lambda s: int(''.join(filter(str.isdigit, s)) or -1))
    sample_names = [f.replace("_peak_table.csv", "") for f in csv_files]

    fwhm_lists, sigma_lists = [], []
    max_peaks = 0
    for f in csv_files:
        df = pd.read_csv(os.path.join(folder, f))
        fwhm_vals = pd.to_numeric(df.get("FWHM", pd.Series()), errors="coerce").to_numpy()
        sigma_vals = pd.to_numeric(df.get("FWHM Sigma", pd.Series()), errors="coerce").to_numpy()
        fwhm_lists.append(fwhm_vals)
        sigma_lists.append(sigma_vals)
        max_peaks = max(max_peaks, len(fwhm_vals))

    if max_peaks == 0:
        print("No valid FWHM data.")
        return

    # Build (n_peaks × n_samples) matrices with NaN padding
    fwhm_arr = np.full((max_peaks, len(csv_files)), np.nan)
    sigma_arr = np.full_like(fwhm_arr, np.nan)

    for j, (fwhm_vals, sig_vals) in enumerate(zip(fwhm_lists, sigma_lists)):
        fwhm_arr[:len(fwhm_vals), j] = fwhm_vals
        sigma_arr[:len(sig_vals), j] = sig_vals

    # ------------------------------------------------------------------ plotting
    plt.figure(figsize=(14, 6))
    for i in range(max_peaks):
        if show_error:
            plt.errorbar(
                sample_names, fwhm_arr[i], yerr=sigma_arr[i],
                marker='o', capsize=3, label=f"Peak {i+1}"
            )
        else:
            plt.plot(sample_names, fwhm_arr[i], marker='o', label=f"Peak {i+1}")

    plt.ylabel("FWHM (°)")
    plt.title("FWHM Drift Across Samples")
    plt.xticks(rotation=45, ha="right")
    plt.grid(False)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.legend(title="Peak", bbox_to_anchor=(1.02, 1), loc='upper left')

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=500)
        print(f"Saved FWHM drift plot to {save_path}")
        plt.close()
    else:
        plt.show()

# ------------------------------------------------------------------
# Intensity drift across samples
# ------------------------------------------------------------------
def plot_intensity_drift_lines(folder, save_path=None, show_error=False):
    """
    Plot intensity drift across samples.
        • folder      – directory that contains *_peak_table.csv files
        • save_path   – PDF/PNG path; if None, show interactively
        • show_error  – if True, add ±sigma error bars
    """
    csv_files = sorted(f for f in os.listdir(folder) if f.endswith("_peak_table.csv"))
    if not csv_files:
        print(f"No peak_table CSVs found in {folder}.")
        return

    # Natural sample order: G101, G102, ...
    csv_files.sort(key=lambda s: int(''.join(filter(str.isdigit, s)) or -1))
    sample_names = [f.replace("_peak_table.csv", "") for f in csv_files]

    intensity_lists, sigma_lists = [], []
    max_peaks = 0
    for f in csv_files:
        df = pd.read_csv(os.path.join(folder, f))
        intensity_vals = pd.to_numeric(df.get("Intensity", pd.Series()), errors="coerce").to_numpy()
        sigma_vals = pd.to_numeric(df.get("Sigma", pd.Series()), errors="coerce").to_numpy()
        intensity_lists.append(intensity_vals)
        sigma_lists.append(sigma_vals)
        max_peaks = max(max_peaks, len(intensity_vals))

    if max_peaks == 0:
        print("No valid Intensity data.")
        return

    # Build (n_peaks × n_samples) matrices with NaN padding
    intensity_arr = np.full((max_peaks, len(csv_files)), np.nan)
    sigma_arr = np.full_like(intensity_arr, np.nan)

    for j, (intensity_vals, sig_vals) in enumerate(zip(intensity_lists, sigma_lists)):
        intensity_arr[:len(intensity_vals), j] = intensity_vals
        sigma_arr[:len(sig_vals), j] = sig_vals

    # ------------------------------------------------------------------ plotting
    plt.figure(figsize=(14, 6))
    for i in range(max_peaks):
        if show_error:
            plt.errorbar(
                sample_names, intensity_arr[i], yerr=sigma_arr[i],
                marker='o', capsize=3, label=f"Peak {i+1}"
            )
        else:
            plt.plot(sample_names, intensity_arr[i], marker='o', label=f"Peak {i+1}")

    plt.ylabel("Intensity (a.u.)")
    plt.title("Intensity Drift Across Samples")
    plt.xticks(rotation=45, ha="right")
    plt.grid(False)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.legend(title="Peak", bbox_to_anchor=(1.02, 1), loc='upper left')

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=500)
        print(f"Saved Intensity drift plot to {save_path}")
        plt.close()
    else:
        plt.show()
