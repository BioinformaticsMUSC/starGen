import os
import re
from collections import defaultdict

def read_config(config_file="config.cfg"):
    config = {}
    with open(config_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    return config

config = read_config()

base_dir = config.get("BASE_DIR", "/path/to/your/fastq")
submission_script = "submit_all.sh"
summary_json = "sample_fastq_map.json"

pattern = re.compile(r"(.+?)(_R?([12])|_read([12]))?_?\d*?\.(fastq|fq)(\.gz)?$")

samples = defaultdict(lambda: {"R1": None, "R2": None})

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith((".fastq", ".fastq.gz", ".fq", ".fq.gz")):
            full_path = os.path.join(root, file)
            match = pattern.match(file)
            if match:
                sample = match.group(1)
                read = match.group(3) or match.group(4)
                if read == "1":
                    samples[sample]["R1"] = full_path
                elif read == "2":
                    samples[sample]["R2"] = full_path
                else:
                    samples[sample]["R1"] = full_path

with open(submission_script, "w") as f:
    f.write("#!/bin/bash\n\n")
    for sample, paths in samples.items():
        r1 = paths["R1"]
        r2 = paths["R2"]
        if r1 and r2:
            f.write(f"sbatch run_star.sh {sample} {r1} {r2}\n")
        elif r1:
            f.write(f"sbatch run_star.sh {sample} {r1}\n")

print(f"Submission script written to: {submission_script}")

import json
with open(summary_json, "w") as f:
    json.dump(samples, f, indent=2)
print(f"JSON sample mapping saved to: {summary_json}")
