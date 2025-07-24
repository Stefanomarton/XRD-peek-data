import pandas as pd
from scipy.stats import ttest_ind

def analyze_crystallinity(csv_path, output_path):
    """
    Analizza la cristallinità e salva i risultati in un file di testo.
    """
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Crystallinity Ratio": "Crystallinity", "Std. Dev.": "StdDev"})

    group1 = df[df["Sample"].str.startswith("G1")]["Crystallinity"]
    group2 = df[df["Sample"].str.startswith("G3")]["Crystallinity"]

    t_stat, p_value = ttest_ind(group1, group2, equal_var=False)

    result = {
        "Group 1 mean": group1.mean(),
        "Group 1 std": group1.std(),
        "Group 2 mean": group2.mean(),
        "Group 2 std": group2.std(),
        "T-statistic": t_stat,
        "P-value": p_value,
    }

    # Scrivi su file in formato leggibile
    with open(output_path, "w") as f:
        f.write("Crystallinity Welch t-test Result\n")
        f.write(f"Group 1 mean: {result['Group 1 mean']:.5f}\n")
        f.write(f"Group 1 std: {result['Group 1 std']:.5f}\n")
        f.write(f"Group 2 mean: {result['Group 2 mean']:.5f}\n")
        f.write(f"Group 2 std: {result['Group 2 std']:.5f}\n")
        f.write(f"T-statistic: {result['T-statistic']:.5f}\n")
        f.write(f"P-value: {result['P-value']:.5f}\n")

    return result
