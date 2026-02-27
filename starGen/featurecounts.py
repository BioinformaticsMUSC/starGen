import os
import glob
import subprocess

def run_featurecounts(base_dir, gtf_file, out_dir="featurecounts_output", threads=8, strand=0, extra_attrs="gene_name"):
    """
    Run featureCounts on all BAM files in base_dir.

    Args:
        base_dir (str): Directory to search for BAMs.
        gtf_file (str): Path to GTF annotation.
        out_dir (str): Output directory.
        threads (int): Number of threads.
        strand (int): Strandness (0=unstranded,1=forward,2=reverse).
        extra_attrs (str): Additional attributes to include in output.
    """
    os.makedirs(out_dir, exist_ok=True)

    bam_pattern = os.path.join(base_dir, "**", "*Aligned.sortedByCoord.out.bam")
    bam_files = glob.glob(bam_pattern, recursive=True)
    if not bam_files:
        print("🚫 No BAM files found in", base_dir)
        return

    output_file = os.path.join(out_dir, "featurecounts_counts.txt")

    featurecounts_commands = (f"featureCounts -T {str(threads)} -a {gtf_file} -o {output_file} "
                              f"-g gene_id -t gene -s {str(strand)} -p {'--extraAttributes ' + extra_attrs if extra_attrs else ''} {' '.join(bam_files)}")
    full_cmd = f"module load biocontainers; module load subread; {featurecounts_commands}"

    print("🚀 Running featureCounts on BAM files...")
    print(full_cmd)

    #result = subprocess.run(cmd, capture_output=True, text=True)
    result = subprocess.run(["bash", "-l", "-c", full_cmd], check=True)
    if result.returncode != 0:
        print("❌ featureCounts failed:")
        print(result.stderr)
    else:
        print("✅ featureCounts completed successfully.")
        print("Counts saved to:", output_file)
