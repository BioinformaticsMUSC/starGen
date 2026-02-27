import os
import json
import re
import pandas as pd
from collections import defaultdict
from .config import load_config

def generate_submission(config_path):
    config = load_config(config_path)
    base_dir = config["BASE_DIR"]

    # Updated pattern to handle both _1/_2 and _R1/_R2 naming conventions
    pattern = re.compile(r"(.+)_([12]|R[12])\.(fastq|fq)(\.gz)?$")
    samples = defaultdict(lambda: {"R1": None, "R2": None})

    print(f"Scanning directory: {base_dir}")
    
    # Check if base directory exists
    if not os.path.exists(base_dir):
        print(f"❌ Error: Directory {base_dir} does not exist!")
        return
    
    processed_files = 0
    total_fastq_files = 0
    
    # First, let's see all FASTQ files in the directory
    for root, _, files in os.walk(base_dir):
        fastq_files_in_dir = [f for f in files if f.endswith((".fastq", ".fastq.gz", ".fq", ".fq.gz"))]
        if fastq_files_in_dir:
            print(f"  Directory: {root}")
            print(f"  Found {len(fastq_files_in_dir)} FASTQ files:")
            for f in fastq_files_in_dir:
                print(f"    - {f}")
            total_fastq_files += len(fastq_files_in_dir)
    
    print(f"\nTotal FASTQ files found: {total_fastq_files}")
    print(f"Attempting to parse with pattern: {pattern.pattern}\n")
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith((".fastq", ".fastq.gz", ".fq", ".fq.gz")):
                full_path = os.path.join(root, file)
                match = pattern.match(file)
                if match:
                    sample = match.group(1)
                    read = match.group(2)
                    # Handle both _1/_2 and _R1/_R2 naming patterns
                    if read in ["1", "R1"]:
                        samples[sample]["R1"] = full_path
                        print(f"  ✓ Found R1 for {sample}: {file}")
                    elif read in ["2", "R2"]:
                        samples[sample]["R2"] = full_path
                        print(f"  ✓ Found R2 for {sample}: {file}")
                    processed_files += 1
                else:
                    print(f"  ⚠️  Skipped (unrecognized pattern): {file}")

    print(f"\nProcessed {processed_files} FASTQ files for {len(samples)} samples.")

    with open("submit_all.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        for sample, paths in samples.items():
            r1 = paths["R1"]
            r2 = paths["R2"]
            if r1 and r2:
                f.write(f"sbatch scripts/run_star.sh {sample} {r1} {r2}\n")
            elif r1:
                f.write(f"sbatch scripts/run_star.sh {sample} {r1}\n")

    with open("sample_fastq_map.json", "w") as f:
        json.dump(samples, f, indent=2)

    print("SLURM script and sample map created.")


def parse_star_log(sample, outdir, summary_csv):
    log_path = os.path.join(outdir, f"{sample}_Log.final.out")
    if not os.path.exists(log_path):
        print(f"❌ No STAR log found for {sample}")
        return

    with open(log_path) as f:
        lines = f.readlines()

    summary = {"Sample": sample}
    for line in lines:
        if "Number of input reads" in line:
            summary["Total_Reads"] = line.strip().split()[-1]
        elif "Uniquely mapped reads %" in line:
            summary["Uniquely_Mapped"] = line.strip().split()[-1]
        elif "% of reads mapped to multiple loci" in line:
            summary["Multi_Mapped"] = line.strip().split()[-1]

    # Append or create CSV
    df = pd.DataFrame([summary])

    if os.path.exists(summary_csv):
        df.to_csv(summary_csv, mode='a', index=False, header=False)
    else:
        df.to_csv(summary_csv, index=False)

    print(f"📊 STAR QC summary written for {sample}")