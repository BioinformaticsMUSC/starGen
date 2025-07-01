# starGen

[![License](https://img.shields.io/github/license/BioinformaticsMUSC/starGen)](LICENSE)

**starGen** is a command-line RNA-seq pipeline focused on STAR alignment, QC visualization, and featureCounts quantification — optimized for SLURM clusters and scalable workflows.

---

## Features

- Generate SLURM batch scripts for STAR alignment  
- Automated per-sample STAR QC summary extraction and visualization (interactive plots & static PNGs)  
- FeatureCounts gene quantification on aligned BAMs  
- Project scaffolding with `starGen init` for easy setup  
- Flexible config-driven workflow, customizable with CLI flags  
- Designed for HPC clusters with SLURM support  

---

## Installation

Install starGen into a conda environment using > python 3.10
```bash
pip install git+https://github.com/BioinformaticsMUSC/starGen.git
```

## Usage

```
# Initialize a new project folder
starGen init my_rnaseq_project

cd my_rnaseq_project

# Modify the config.cfg file (see below)

# Generate SLURM scripts for STAR alignment
starGen generate --config config.cfg

# Submit jobs (via SLURM)
bash submit_all.sh

# Visualize STAR QC metrics after alignments
starGen qc

# Run featureCounts quantification on BAM files
starGen featurecounts --gtf-file /path/to/annotation.gtf
```

## Configuration
Your config.cfg file should be updated with the following information:
```
BASE_DIR=./fastqs
STAR_INDEX=/path/to/star/index
GTF_FILE=/path/to/annotation.gtf

```

