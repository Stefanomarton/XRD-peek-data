import os
import re
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO


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


# ------------------------------------------------------------------
# Crystallinity (ratio & propagated standard deviation)
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# Crystallinity (ratio & std dev from scatter of peak contributions)
# ------------------------------------------------------------------
def compute_crystallinity_ratio(ref_path, numerator_peaks, total_peaks):
    """
    Return (ratio, std_dev):
        ratio    = sum(I_selected) / sum(I_all)
        std_dev  = std‑dev of individual peak‑ratios   I_i / sum(I_all)
    numerator_peaks – list of 1‑based peak indices to include in numerator.
    """
    positions, intensities, _sigmas, *_ = extract_peaks_from_ref(ref_path, total_peaks)

    if not intensities:
        raise ValueError(f"No peaks parsed from {ref_path}")

    max_req = max(numerator_peaks)
    if len(intensities) < max_req:
        raise ValueError(
            f"{os.path.basename(ref_path)} has {len(intensities)} peaks; "
            f"requested peak index {max_req}"
        )

    total_intensity = float(sum(intensities))
    if total_intensity == 0:
        return 0.0, 0.0

    # Overall crystallinity ratio
    numerator = sum(intensities[i - 1] for i in numerator_peaks)
    ratio = numerator / total_intensity

    # Build list of individual peak‑ratios, then std dev of that list
    peak_ratios = [intensities[i - 1] / total_intensity for i in numerator_peaks]
    std_dev = float(np.std(peak_ratios, ddof=0))   # population std‑dev

    return ratio, std_dev



# ------------------------------------------------------------------
# Crystallinity summary plot (group‑mean bands and group‑coloured points)
# ------------------------------------------------------------------
def plot_crystallinity_summary(csv_path, save_path=None):
    """
    • per‑sample error bars
      – G1xx  → blue points
      – G3xx  → orange points
    • group means ± 1 σ as shaded bands + dashed lines
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    df = pd.read_csv(csv_path)

    # Natural numeric sort  (G101, G102, …)
    df["Sample_num"] = df["Sample"].str.extract(r"(\d+)").astype(int)
    df = df.sort_values("Sample_num").reset_index(drop=True)

    x = np.arange(len(df))  # x‑axis positions

    # Masks
    g1_mask = df["Sample"].str.startswith("G1")
    g3_mask = df["Sample"].str.startswith("G3")

    # Group stats
    mean_g1 = df.loc[g1_mask, "Crystallinity Ratio"].mean()
    std_g1  = df.loc[g1_mask, "Crystallinity Ratio"].std(ddof=0)

    mean_g3 = df.loc[g3_mask, "Crystallinity Ratio"].mean()
    std_g3  = df.loc[g3_mask, "Crystallinity Ratio"].std(ddof=0)

    # ------------------------------------------------ plotting
    plt.figure(figsize=(12, 6))

    # Shaded ±1 σ bands
    full_span = [-0.5, len(df) - 0.5]
    plt.fill_between(full_span, mean_g1 - std_g1, mean_g1 + std_g1,
                     color="tab:blue", alpha=0.15, zorder=0, label="G1xx ±1σ")
    plt.fill_between(full_span, mean_g3 - std_g3, mean_g3 + std_g3,
                     color="tab:orange", alpha=0.15, zorder=0, label="G3xx ±1σ")

    # Mean lines
    plt.axhline(mean_g1, color="tab:blue", linestyle="--",
                linewidth=1.5, label=f"G1xx mean = {mean_g1:.3f}")
    plt.axhline(mean_g3, color="tab:orange", linestyle="--",
                linewidth=1.5, label=f"G3xx mean = {mean_g3:.3f}")

    # Per‑sample points with error bars, coloured by group
    plt.errorbar(
        x[g1_mask], df.loc[g1_mask, "Crystallinity Ratio"],
        yerr=df.loc[g1_mask, "Std. Dev."],
        fmt='o', color="tab:blue", ecolor="tab:gray",
        capsize=4, label="G1xx samples", zorder=3
    )
    plt.errorbar(
        x[g3_mask], df.loc[g3_mask, "Crystallinity Ratio"],
        yerr=df.loc[g3_mask, "Std. Dev."],
        fmt='o', color="tab:orange", ecolor="tab:gray",
        capsize=4, label="G3xx samples", zorder=3
    )

    # Axis cosmetics
    plt.xticks(x, df["Sample"], rotation=90)
    plt.ylabel("Crystallinity Ratio")
    plt.title("Crystallinity Ratio — group means ±1 σ")
    plt.grid(False)
    plt.legend()
    plt.tight_layout()

    # Save / show
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=500)
        print(f"Saved crystallinity summary plot to {save_path}")
        plt.close()
    else:
        plt.show()




# ------------------------------------------------------------------
# Per-sample plot (peaks + calc + experimental + residuals)
# ------------------------------------------------------------------
def plot_from_directory(
    directory,
    save=False,
    outdir=None,
    show_residuals=True,
    show_table=True,
    crystallinity_peaks=None,
    crystallinity_summary=None,
):
    """
    Plot one sample folder: peak_x.xy components, wpl_fit.cal (sum),
    experimental G*.xy or G*.dat, residuals, and optional CSV exports.
    """
    # Gather file paths
    peak_paths = sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith("peak_") and f.endswith(".xy")
    )
    calc_sum_path = next(
        (os.path.join(directory, f) for f in os.listdir(directory) if f.endswith("wpl_fit.cal")),
        None
    )
    experimental_path = next(
        (os.path.join(directory, f) for f in os.listdir(directory)
         if f.startswith("G") and (f.endswith(".xy") or f.endswith(".dat"))),
        None
    )
    ref_path = next(
        (os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".REF")),
        None
    )

    if not peak_paths or calc_sum_path is None or experimental_path is None:
        raise FileNotFoundError(f"Missing required files in {directory}")

    # Load peaks
    peak_data = [load_xy(p) for p in peak_paths]
    all_x = np.concatenate([d[:, 0] for d in peak_data])
    x_common = np.linspace(all_x.min(), all_x.max(), 4000)
    y_total = np.zeros_like(x_common)

    # Figure layout
    if show_residuals:
        fig, axes = plt.subplots(
            nrows=2, figsize=(10, 6), sharex=True,
            gridspec_kw={'height_ratios': [3, 1]}
        )
        ax1, ax2 = axes
    else:
        fig, ax1 = plt.subplots(figsize=(10, 4))
        ax2 = None

    # Plot peak components
    for pth, data in zip(peak_paths, peak_data):
        x_peak, y_peak = data[:, 0], data[:, 1]
        y_interp = np.interp(x_common, x_peak, y_peak)
        y_total += y_interp
        ax1.plot(x_peak, y_peak, '--', label=os.path.basename(pth).replace('.xy', ''))

    # Plot calculated sum
    x_calc, y_calc = load_xy(calc_sum_path).T
    ax1.plot(x_calc, y_calc, 'k-', linewidth=1.2, label='Calculated')

    # Experimental
    x_exp, y_exp = load_xy(experimental_path).T
    ax1.plot(x_exp, y_exp, 'r-', alpha=0.5, label='Experimental')

    name = os.path.basename(directory.rstrip("/"))

    ax1.set_ylabel('Intensity (a.u.)')
    ax1.set_title(f'{name} — Peak Fit')
    ax1.legend(fontsize='small')
    ax1.grid(False)

    # Residuals (restricted to calc range)
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

    # Save figure & exports
    outdir = outdir or directory
    os.makedirs(outdir, exist_ok=True)

    if save:
        pdf_path = os.path.join(outdir, f"{name}_fit_plot.png")
        plt.savefig(pdf_path, bbox_inches="tight", dpi=500)
        print(f"Saved plot PDF: {pdf_path}")

        if show_table and ref_path:
            save_peak_table_csv(directory, ref_path, len(peak_paths), outdir)

        if crystallinity_peaks and ref_path:
            ratio, std_dev = compute_crystallinity_ratio(ref_path, crystallinity_peaks, len(peak_paths))
            if crystallinity_summary is not None:
                crystallinity_summary.append((name, ratio, std_dev))

    plt.close(fig)


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

# ------------------------------------------------------------------
# Batch driver
# ------------------------------------------------------------------
def batch_plot(
    root_dir,
    save=True,
    show_residuals=True,
    output_dir=None,
    show_table=True,
    crystallinity_peaks=None,
):
    """
    Process all subdirectories under root_dir.
    Generates per-sample fit PDFs & peak tables;
    crystallinity summary CSV + plot;
    peak position & FWHM drift plots.
    """
    summary = []

    subdirs = [
        os.path.join(root_dir, d)
        for d in sorted(os.listdir(root_dir))
        if os.path.isdir(os.path.join(root_dir, d))
    ]

    for subdir in subdirs:
        try:
            name = os.path.basename(subdir.rstrip("/"))
            outdir = output_dir if output_dir else subdir
            os.makedirs(outdir, exist_ok=True)

            print(f"Processing: {subdir}")
            plot_from_directory(
                directory=subdir,
                save=save,
                outdir=outdir,
                show_residuals=show_residuals,
                show_table=show_table,
                crystallinity_peaks=crystallinity_peaks,
                crystallinity_summary=summary,
            )
        except Exception as e:
            print(f"Skipped {subdir}: {e}")

    final_outdir = output_dir or root_dir
    os.makedirs(final_outdir, exist_ok=True)

    # Crystallinity summary
    if summary:
        # ------------------------------------------
        # ➊  Build group‑wise lists of ratios
        # ------------------------------------------
        group_dict = {"G1": [], "G3": []}          # add more keys if needed
        for sample, ratio, _ in summary:           # ignore the old per‑sample std
            prefix = "G3" if sample.startswith("G3") else "G1"
            group_dict[prefix].append(ratio)

        # Compute population std‑dev for each group
        group_std = {g: float(np.std(vals, ddof=0)) for g, vals in group_dict.items()}

        # ------------------------------------------
        # ➋  Write CSV with group std‑dev
        # ------------------------------------------
        csv_path = os.path.join(final_outdir, "crystallinity_summary.csv")
        with open(csv_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sample", "Crystallinity Ratio", "Std. Dev."])
            for sample, ratio, _ in summary:
                prefix = "G3" if sample.startswith("G3") else "G1"
                writer.writerow([sample, f"{ratio:.5f}", f"{group_std[prefix]:.5f}"])
                
       # ------------------------------- plot -------------------------------------
        plot_path = os.path.join(final_outdir, "crystallinity_summary_plot.png")
        plot_crystallinity_summary(csv_path, save_path=plot_path)
    


    # Peak position drift
    peak_pos_plot = os.path.join(final_outdir, "peak_position_drift.png")
    plot_peak_position_drift(final_outdir, save_path=peak_pos_plot)

    # FWHM drift
    fwhm_plot = os.path.join(final_outdir, "fwhm_drift_plot.png")
    plot_fwhm_drift_lines(final_outdir, save_path=fwhm_plot, show_error=True)

        # FWHM drift
    intensity_plot = os.path.join(final_outdir, "intensity_drift.png")
    plot_intensity_drift_lines(final_outdir, save_path=intensity_plot, show_error=True)

    plt.close('all')  # extra safety


# ------------------------------------------------------------------
# __main__
# ------------------------------------------------------------------
if __name__ == "__main__":
    batch_plot(
        root_dir="../../data",
        save=True,
        show_residuals=True,
        output_dir="../../results",
        show_table=True,
        crystallinity_peaks=[1, 2, 3, 4, 5, 6],
    )
