import click
from .init import init_project
from .generator import generate_submission
from .qc import visualize_star_qc
from .featurecounts import run_featurecounts

@click.group()
def cli():
    """STAR Pipeline CLI: SLURM-ready RNA-seq workflows."""
    pass

@cli.command()
@click.argument("project_name")
def init(project_name):
    """Initialize a new STAR project directory."""
    init_project(project_name)

@cli.command()
@click.option("--config", default="config.cfg", help="Path to config file.")
def generate(config):
    """Generate SLURM STAR submission script."""
    generate_submission(config)

@cli.command()
@click.option("--summary", default="star_output/STAR_summary.csv", help="Path to STAR summary file.")
@click.option("--out-dir", default="star_output/qc_plots", help="Output folder for plots.")
@click.option("--min-unique", default=70)
@click.option("--max-multi", default=10)
def qc(summary, out_dir, min_unique, max_multi):
    """Visualize STAR alignment QC."""
    visualize_star_qc(summary_path=summary, out_dir=out_dir, min_unique=min_unique, max_multi=max_multi)

from .config import load_config
import os

def print_featurecounts_command(base_dir, gtf_file, out_dir, threads, strand):
    import glob
    bam_pattern = os.path.join(base_dir, "**", "*Aligned.sortedByCoord.out.bam")
    bam_files = glob.glob(bam_pattern, recursive=True)
    if not bam_files:
        print("🚫 No BAM files found in", base_dir)
        return

    cmd = [
        "featureCounts",
        "-T", str(threads),
        "-a", gtf_file,
        "-o", os.path.join(out_dir, "featurecounts_counts.txt"),
        "-g", "gene_id",
        "-t", "exon",
        "-s", str(strand),
    ] + bam_files

    print(" ".join(cmd))

@cli.command()
@click.option("--base-dir", default="star_output", help="Directory with BAM files.")
@click.option("--gtf-file", default=None, help="Path to annotation GTF file (overrides config).")
@click.option("--config", default="config.cfg", help="Path to project config file.")
@click.option("--out-dir", default="featurecounts_output", help="Output directory.")
@click.option("--threads", default=8, help="Number of threads.")
@click.option("--strand", default=0, type=int, help="Strandness (0=unstranded).")
@click.option("--dry-run", is_flag=True, help="Show the command without running featureCounts.")
def featurecounts(base_dir, gtf_file, config, out_dir, threads, strand, dry_run):
    """Run featureCounts on all BAM files in a project."""

    # Load config if needed
    if gtf_file is None:
        cfg = load_config(config)
        if "GTF_FILE" not in cfg:
            print("❌ ERROR: GTF_FILE not set in config and --gtf-file not provided.")
            return
        gtf_file = cfg["GTF_FILE"]

    # Validate GTF path
    if not os.path.exists(gtf_file):
        print(f"❌ ERROR: GTF file not found: {gtf_file}")
        return

    # Instead of running, just print the command if dry-run
    if dry_run:
        print("Dry run mode: command that would be executed:")
        print_featurecounts_command(base_dir, gtf_file, out_dir, threads, strand)
    else:
        run_featurecounts(base_dir, gtf_file, out_dir, threads, strand)



if __name__ == "__main__":
    cli()
