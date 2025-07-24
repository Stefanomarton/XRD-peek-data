import os
import csv
import numpy as np
import matplotlib.pyplot as plt


from core import plot_from_directory, create_peak_table_csv
from cristallinity import plot_crystallinity_summary, calculate_crystallinity_from_csv
from drifts import plot_drift
from scatter import plot_peak_metrics_vs_crystallinity
from stats import analyze_crystallinity

# ------------------------------------------------------------------
# Batch driver
# ------------------------------------------------------------------
def batch_plot(
    root_dir,
    show_residuals=True,
    output_dir=None,
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
                outdir=outdir,
                show_residuals=show_residuals,
            )
            csv_path = create_peak_table_csv(subdir, outdir=outdir)
            # if csv_path:
            #     calculate_crystallinity_from_csv(csv_path, crystallinity_peaks, crystallinity_summary=summary)

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

        crystallinity_stats = os.path.join(final_outdir, "crystallinity_stats.txt")
        analyze_crystallinity(csv_path, crystallinity_stats)

    plt.close('all')  # extra safety


def batch_crystallinity_series(root_dir, output_dir=None, max_peaks=7):
    """
    For each number of crystallinity peaks from 1 to max_peaks,
    compute, save and plot crystallinity summary across samples.
    """
    import os
    os.makedirs(output_dir or root_dir, exist_ok=True)
    final_outdir = output_dir or root_dir

    subdirs = [
        os.path.join(root_dir, d)
        for d in sorted(os.listdir(root_dir))
        if os.path.isdir(os.path.join(root_dir, d))
    ]

    for k in range(1, max_peaks + 1):
        print(f"\n[INFO] ---> Computing crystallinity with peaks [1..{k}]")
        crystallinity_peaks = list(range(1, k + 1))
        summary = []

        for subdir in subdirs:
            try:
                name = os.path.basename(subdir.rstrip("/"))
                outdir = final_outdir  # use flat output dir for all
                os.makedirs(outdir, exist_ok=True)

                csv_path = create_peak_table_csv(subdir, outdir=outdir)
                if csv_path:
                    calculate_crystallinity_from_csv(csv_path, crystallinity_peaks, crystallinity_summary=summary)
            except Exception as e:
                print(f"[WARN] {subdir}: {e}")

        # Group & write summary
        if summary:
            group_dict = {"G1": [], "G3": []}
            for sample, ratio, _ in summary:
                prefix = "G3" if sample.startswith("G3") else "G1"
                group_dict[prefix].append(ratio)
            group_std = {g: float(np.std(vals, ddof=0)) for g, vals in group_dict.items()}

            # CSV output
            csv_path = os.path.join(final_outdir, f"crystallinity_summary_{k}.csv")
            with open(csv_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Sample", "Crystallinity Ratio", "Std. Dev."])
                for sample, ratio, _ in summary:
                    prefix = "G3" if sample.startswith("G3") else "G1"
                    writer.writerow([sample, f"{ratio:.5f}", f"{group_std[prefix]:.5f}"])

            # Plot
            plot_path = os.path.join(final_outdir, f"crystallinity_summary_{k}_plot.png")
            plot_crystallinity_summary(csv_path, save_path=plot_path)

            # Text analysis
            stats_path = os.path.join(final_outdir, f"crystallinity_stats_{k}.txt")
            analyze_crystallinity(csv_path, stats_path)

# ------------------------------------------------------------------
# __main__
# ------------------------------------------------------------------
if __name__ == "__main__":
    
    batch_plot(
        root_dir="../../data",
        show_residuals=True,
        output_dir="../../results",
        crystallinity_peaks=[1, 2, 3, 4, 5, 6, 7],
    )

    plot_drift(output_dir="../../results")
    
    batch_crystallinity_series(
        root_dir="../../data",
        output_dir="../../results",
        max_peaks=7,
    )
    
    plot_peak_metrics_vs_crystallinity("../../results")

