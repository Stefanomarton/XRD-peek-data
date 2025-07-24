import os
import numpy as np

from core import extract_peaks_from_ref


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
