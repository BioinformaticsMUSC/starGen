import pandas as pd
import plotly.express as px
import os

def visualize_star_qc(summary_path="star_output/STAR_summary.csv", out_dir="star_output/qc_plots", min_unique=70, max_multi=10):
    os.makedirs(out_dir, exist_ok=True)

    # Load and clean data
    df = pd.read_csv(summary_path)
    df["Uniquely_Mapped"] = df["Uniquely_Mapped"].str.replace('%', '').astype(float)
    df["Multi_Mapped"] = df["Multi_Mapped"].str.replace('%', '').astype(float)

    def flag(row):
        if row["Uniquely_Mapped"] < min_unique or row["Multi_Mapped"] > max_multi:
            return "❌ Low Quality"
        return "✅ OK"

    df["QC_Flag"] = df.apply(flag, axis=1)

    # Plot 1: Total Reads
    fig1 = px.bar(
        df,
        x="Sample",
        y="Total_Reads",
        color="QC_Flag",
        title="Total Reads per Sample",
        text="Total_Reads",
        color_discrete_map={"✅ OK": "green", "❌ Low Quality": "red"}
    )
    fig1.update_layout(xaxis_tickangle=-45)
    fig1.write_image(f"{out_dir}/total_reads.png", width=1000, height=600)
    fig1.write_html(f"{out_dir}/total_reads.html")

    # Plot 2: Mapping %
    fig2 = px.bar(
        df,
        x="Sample",
        y=["Uniquely_Mapped", "Multi_Mapped"],
        color="QC_Flag",
        barmode="group",
        title="Mapping Rates per Sample",
        text_auto=".1f",
        color_discrete_map={"✅ OK": "blue", "❌ Low Quality": "orange"}
    )
    fig2.update_layout(xaxis_tickangle=-45, yaxis_title="Percent (%)")
    fig2.write_image(f"{out_dir}/mapping_rates.png", width=1000, height=600)
    fig2.write_html(f"{out_dir}/mapping_rates.html")

    # Save flagged samples
    flagged = df[df["QC_Flag"] == "❌ Low Quality"]
    flagged.to_csv(f"{out_dir}/low_quality_samples.csv", index=False)

    print("✅ STAR QC plots and summary saved to:", out_dir)

import os
import re

def parse_star_log(filepath):
    """
    Parses a STAR Log.final.out file and returns key metrics as a dictionary.
    """
    sample = os.path.basename(filepath).split(".")[0]
    results = {
        "sample": sample,
        "input_reads": None,
        "uniquely_mapped_reads": None,
        "uniquely_mapped_percent": None,
        "multimapped_reads": None,
        "multimapped_percent": None,
        "unmapped_percent": None,
    }

    with open(filepath, "r") as f:
        for line in f:
            if "Number of input reads" in line:
                results["input_reads"] = int(line.split("|")[1].strip())
            elif "Uniquely mapped reads number" in line:
                results["uniquely_mapped_reads"] = int(line.split("|")[1].strip())
            elif "Uniquely mapped reads %" in line:
                results["uniquely_mapped_percent"] = float(line.split("|")[1].strip().replace("%", ""))
            elif "Number of reads mapped to multiple loci" in line:
                results["multimapped_reads"] = int(line.split("|")[1].strip())
            elif "% of reads mapped to multiple loci" in line:
                results["multimapped_percent"] = float(line.split("|")[1].strip().replace("%", ""))
            elif "% of reads unmapped: too many mismatches" in line:
                # We'll sum all unmapped percentages at the end
                if results["unmapped_percent"] is None:
                    results["unmapped_percent"] = 0.0
                results["unmapped_percent"] += float(line.split("|")[1].strip().replace("%", ""))
            elif "% of reads unmapped: too short" in line:
                results["unmapped_percent"] += float(line.split("|")[1].strip().replace("%", ""))
            elif "% of reads unmapped: other" in line:
                results["unmapped_percent"] += float(line.split("|")[1].strip().replace("%", ""))

    return results
