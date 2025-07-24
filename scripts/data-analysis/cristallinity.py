import os
import numpy as np
import pandas as pd

from core import save_peak_table_csv

# ------------------------------------------------------------------
# Crystallinity (ratio & std dev from scatter of peak contributions)
#   – version that reads the *_peak_table.csv* produced by
#     save_peak_table_csv rather than the original .REF file
# ------------------------------------------------------------------

def compute_crystallinity_ratio(csv_path, numerator_peaks):
    """
    Return (ratio, std_dev):
        ratio    = sum(I_selected) / sum(I_all)
        std_dev  = std-dev of individual peak-ratios   I_i / sum(I_all)

    Parameters
    ----------
    csv_path : str
        Path to the CSV created by `save_peak_table_csv` for one sample.
        The file must contain an 'Intensity' column.
    numerator_peaks : list[int]
        1-based indices of the peaks that belong in the numerator.

    Notes
    -----
    * The order of rows in the CSV is treated exactly like the peak
      order in the REF file used to be, so the same index list works.
    * Any rows whose intensity is NaN or zero are ignored.
    """

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(csv_path)

    # read only the intensities column
    intensities = pd.read_csv(csv_path, usecols=['Intensity'])['Intensity'].to_numpy()

    # filter out any NaN values that might slip in
    intensities = intensities[~np.isnan(intensities)]

    if intensities.size == 0:
        raise ValueError(f"No intensities found in {csv_path}")

    max_req = max(numerator_peaks)
    if intensities.size < max_req:
        raise ValueError(
            f"{os.path.basename(csv_path)} has {intensities.size} peaks; "
            f"requested peak index {max_req}"
        )

    total_intensity = float(intensities.sum())
    if total_intensity == 0:
        return 0.0, 0.0

    numerator = float(sum(intensities[i - 1] for i in numerator_peaks))
    ratio = numerator / total_intensity

    # peak-specific ratios for the population σ
    peak_ratios = [float(intensities[i - 1] / total_intensity) for i in numerator_peaks]
    std_dev = float(np.std(peak_ratios, ddof=0))

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


def calculate_crystallinity_from_csv(csv_path, crystallinity_peaks, crystallinity_summary=None):
    """
    Compute crystallinity ratio from a peak table CSV.
    Append result to summary if provided.
    """
    import os

    if not crystallinity_peaks or not os.path.isfile(csv_path):
        return None

    name = os.path.basename(csv_path).replace("_peak_table.csv", "")
    ratio, std_dev = compute_crystallinity_ratio(csv_path, crystallinity_peaks)

    if crystallinity_summary is not None:
        crystallinity_summary.append((name, ratio, std_dev))

    return ratio, std_dev



