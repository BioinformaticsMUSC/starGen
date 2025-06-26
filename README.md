# starGen
Generates scripts for finding fastQ files and generating STAR alignment scripts

---

## Overview

- `config.cfg`: Set your base FASTQ directory and STAR index path here.
- `generate_submission.py`: Scans FASTQ files, creates a SLURM submission script `submit_all.sh`.
- `run_star.sh`: SLURM batch script that runs STAR using settings from `config.cfg`.
- `submit_all.sh`: Auto-generated script to submit jobs for all samples.
- `sample_fastq_map.json`: JSON mapping of samples to FASTQ files (generated).
- `STAR_summary.csv`: STAR alignment QC summary (generated).
- `logs/`: Directory for SLURM job logs.
- `star_output/`: Directory for STAR output BAM files and logs.

---

## Setup

1. **Edit `config.cfg`**

```bash
# config.cfg
BASE_DIR=/path/to/your/fastq
STAR_INDEX=/path/to/your/star/index
```

2. **Make scripts executable and create logs directory**

```bash
chmod -x run_star.sh generate_submission.py
mkdir -p logs
```
---

## Usage

1. **Generate slurm script based on your FASTQ files**
```bash
python generate_submission.py
```

2. **Submit jobs to SLURM**
```bash
bash submit_all.sh
```
