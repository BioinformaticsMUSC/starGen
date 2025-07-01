#!/bin/bash
#SBATCH --job-name=star_align
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G

# Load config file - adjust path if config.cfg is in a different location
source config.cfg

# Arguments
SAMPLE=$1
R1=$2
R2=$3

OUTDIR="${BASE_DIR}/star_output/${SAMPLE}"
LOG_SUMMARY="${OUTDIR}/${SAMPLE}_STAR_Log.final.out"
SUMMARY_CSV="${BASE_DIR}/star_output/STAR_summary.csv"

mkdir -p "$OUTDIR"

# Load STAR module (adjust for your environment)
module load STAR/2.7.10a

if [ -n "$R2" ]; then
  echo "Running STAR for paired-end: $SAMPLE"
  STAR --runThreadN 8 \
       --genomeDir "$STAR_INDEX" \
       --readFilesIn "$R1" "$R2" \
       --readFilesCommand zcat \
       --outFileNamePrefix "${OUTDIR}/${SAMPLE}_" \
       --outSAMtype BAM SortedByCoordinate
else
  echo "Running STAR for single-end: $SAMPLE"
  STAR --runThreadN 8 \
       --genomeDir "$STAR_INDEX" \
       --readFilesIn "$R1" \
       --readFilesCommand zcat \
       --outFileNamePrefix "${OUTDIR}/${SAMPLE}_" \
       --outSAMtype BAM SortedByCoordinate
fi

if [ -f "$LOG_SUMMARY" ]; then
  TOTAL_READS=$(grep "Number of input reads" "$LOG_SUMMARY" | awk '{print $NF}')
  UNIQUELY_MAPPED=$(grep "Uniquely mapped reads %" "$LOG_SUMMARY" | awk '{print $(NF-1) $NF}')
  MULTI_MAPPED=$(grep "% of reads mapped to multiple loci" "$LOG_SUMMARY" | awk '{print $(NF-1) $NF}')

  if [ ! -f "$SUMMARY_CSV" ]; then
    echo "Sample,Total_Reads,Uniquely_Mapped,Multi_Mapped" > "$SUMMARY_CSV"
  fi

  echo -e "${SAMPLE},${TOTAL_READS},${UNIQUELY_MAPPED},${MULTI_MAPPED}" >> "$SUMMARY_CSV"
fi
