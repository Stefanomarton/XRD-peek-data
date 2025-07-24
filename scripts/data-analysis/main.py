import os
import csv
import numpy as np
import matplotlib.pyplot as plt


from core import load_xy, save_peak_table_csv
from cristallinity import compute_crystallinity_ratio, plot_crystallinity_summary
from drifts import plot_fwhm_drift_lines, plot_intensity_drift_lines, plot_peak_position_drift
from scatter import plot_peak_metrics_vs_crystallinity

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
    plot_fwhm_drift_lines(final_outdir, save_path=fwhm_plot, show_error=False)

        # FWHM drift
    intensity_plot = os.path.join(final_outdir, "intensity_drift.png")
    plot_intensity_drift_lines(final_outdir, save_path=intensity_plot, show_error=False)

    # Peak-metric vs crystallinity scatter plots
    plot_peak_metrics_vs_crystallinity(final_outdir)

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
        crystallinity_peaks=[1, 2, 3, 4, 5, 6, 7],
    )
