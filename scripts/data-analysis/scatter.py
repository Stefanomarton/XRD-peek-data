import os
import re
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib import cm

# ------------------------------------------------------------------
# Peak-metric vs Crystallinity  (2×4 grid, 8 colours)
# ------------------------------------------------------------------
def plot_peak_metrics_vs_crystallinity(folder, summary_csv="crystallinity_summary.csv"):
    cpath = os.path.join(folder, summary_csv)
    if not os.path.exists(cpath):
        print(f"[peak-metrics] Missing {cpath}")
        return
    cdf = pd.read_csv(cpath)

    peak_files = [f for f in os.listdir(folder) if f.endswith("_peak_table.csv")]
    if not peak_files:
        print("[peak-metrics] No *_peak_table.csv files.")
        return
    peak_files.sort(key=lambda s: int("".join(filter(str.isdigit, s)) or -1))

    # ── long-format df ───────────────────────────────────────────────
    records = []
    for pf in peak_files:
        samp = pf.replace("_peak_table.csv", "")
        df   = pd.read_csv(os.path.join(folder, pf))
        for idx in range(len(df)):
            records.append(
                dict(
                    Sample    = samp,
                    Peak      = idx + 1,
                    Intensity = df.at[idx, "Intensity"],
                    Position  = df.at[idx, "Position (°)"],
                    FWHM      = df.at[idx, "FWHM"],
                )
            )
    peak_df = pd.DataFrame.from_records(records)
    merged  = peak_df.merge(cdf[["Sample", "Crystallinity Ratio"]], on="Sample", how="inner")
    if merged.empty:
        print("[peak-metrics] No overlap between peaks and summary.")
        return

    # Fixed palette: tab10 first 8 colours
    palette = list(plt.get_cmap("tab10").colors[:8])

    # ── helper: 2×4 collage ─────────────────────────────────────────
    def collage(metric, xlabel, out_png, logx=False):
        peaks  = sorted(merged["Peak"].unique())[:8]   # only first 8
        fig, axes = plt.subplots(2, 4, figsize=(16, 6), sharey=True)
        axes = axes.ravel()

        # Blank unused slots if < 8 peaks
        for ax in axes[len(peaks):]:
            ax.axis("off")

        for i, pk in enumerate(peaks):
            ax  = axes[i]
            sub = merged[merged["Peak"] == pk]
            ax.scatter(sub[metric], sub["Crystallinity Ratio"],
                       color=palette[i], edgecolor="k", s=40)
            if logx:
                ax.set_xscale("log")
                ax.minorticks_off()
            ax.set_title(f"Peak {pk}")
            ax.grid(False)
            if i % 4 == 0:
                ax.set_ylabel("Crystallinity")
            if i >= 4:                # bottom row
                ax.set_xlabel(xlabel)

        fig.suptitle(f"Crystallinity vs {xlabel}", fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.94])
        path = os.path.join(folder, out_png)
        fig.savefig(path, dpi=500, bbox_inches="tight")
        print("Saved", path)
        plt.close(fig)

    # ── generate the three collages ─────────────────────────────────
    collage("Intensity", "Intensity (a.u.)", "crystallinity_vs_intensity.png", logx=False)
    collage("Position",  "Position (°)",     "crystallinity_vs_position.png",  logx=False)
    collage("FWHM",      "FWHM (°)",         "crystallinity_vs_fwhm.png",      logx=False)
