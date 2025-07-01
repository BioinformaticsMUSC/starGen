import os
import tempfile

from starGen.generator import generate_submission
from starGen.init import init_project

# Helper: create a fake config.cfg
def create_test_config(path):
    config_content = """BASE_DIR=./test_fastqs
STAR_INDEX=/test/index
GTF_FILE=/test/gtf.gtf
"""
    with open(path, "w") as f:
        f.write(config_content)

# Helper: create fake FASTQs to simulate sample detection
def create_fake_fastqs(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    with open(os.path.join(base_dir, "SAMPLE1_R1.fq"), "w") as f:
        f.write("FAKESEQ")
    with open(os.path.join(base_dir, "SAMPLE1_R2.fq"), "w") as f:
        f.write("FAKESEQ")

def test_generate_submission_creates_scripts():
    # Use a temp dir for the whole test
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.cfg")
        fastq_dir = os.path.join(tmpdir, "test_fastqs")

        create_test_config(config_path)
        create_fake_fastqs(fastq_dir)

        # Change to the temp dir so paths work
        cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            init_project(project_name="TMP")
            project_dir = os.path.join(tmpdir, "TMP")
            generate_submission(config_path=config_path)

            # Check that submit_all.sh was created
            submit_path = os.path.join(tmpdir, "submit_all.sh")
            assert os.path.exists(submit_path)

            with open(submit_path) as f:
                contents = f.read()
                assert "sbatch scripts/run_star.sh SAMPLE1" in contents

            # Check that run_star.sh script was created
            slurm_script = os.path.join(project_dir, "scripts", "run_star.sh")
            assert os.path.exists(slurm_script)
            with open(slurm_script) as f:
                script_text = f.read()
                assert "--readFilesIn" in script_text
                assert "STAR" in script_text

        finally:
            os.chdir(cwd)  # Always go back to the real cwd
