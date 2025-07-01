import os
import shutil
from importlib.resources import files

def init_project(project_name):
    print(f"Initializing STAR pipeline project: {project_name}")
    os.makedirs(project_name, exist_ok=True)

    # Create scripts directory
    scripts_dir = os.path.join(project_name, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    # Copy run_star.sh
    run_star_src = files("starGen").joinpath("scripts/run_star.sh")
    run_star_dst = os.path.join(scripts_dir, "run_star.sh")
    shutil.copy(run_star_src, run_star_dst)

    # Create config.cfg
    config_path = os.path.join(project_name, "config.cfg")
    with open(config_path, "w") as f:
        f.write("""# STAR pipeline config
BASE_DIR=./fastqs
STAR_INDEX=/path/to/star/index
GTF_FILE=/path/to/annotation.gtf
""")

    # Create .gitignore
    with open(os.path.join(project_name, ".gitignore"), "w") as f:
        f.write("*.out\n*.err\n*.log\nstar_output/\nsubmit_all.sh\nsample_fastq_map.json\n")

    print(f"✅ Project created at: {project_name}")
    print("📄 To get started:")
    print(f"   cd {project_name}")
    print("   star-pipeline generate --config config.cfg")
