import json
import logging
import os
import sys
import traceback
import zipfile
from typing import Any

from my_proof.proof import Proof

INPUT_DIR = os.environ.get("INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/output")

logging.basicConfig(level=logging.INFO, format="%(message)s")


def load_config() -> dict[str, Any]:
    """Load proof configuration from environment variables."""
    config = {
        "dlp_id": os.environ.get("DLP_ID"),  # Set your own DLP ID here
        "input_dir": INPUT_DIR,
        "db_uri": os.environ.get(
            "DB_URI", "postgresql+psycopg://postgres:root@localhost/audata"
        ),
        "path_to_yaml": "audata_proof/model/model_config_RawNet.yaml",
        "path_to_model": "audata_proof/model/model.pth",
    }
    logging.info(f"Using config: {json.dumps(config, indent=2)}")
    return config


def run() -> None:
    """Generate proofs for all input files."""
    config = load_config()
    input_files_exist = os.path.isdir(INPUT_DIR) and bool(os.listdir(INPUT_DIR))

    if not input_files_exist:
        raise FileNotFoundError(f"No input files found in {INPUT_DIR}")
    extract_input()

    proof = Proof(config)
    proof_response = proof.generate()

    output_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(output_path, "w") as f:
        json.dump(proof_response.model_dump(), f, indent=2)
    logging.info(f"Proof generation complete: {proof_response}")


def extract_input() -> None:
    """
    If the input directory contains any zip files, extract them
    :return:
    """
    for input_filename in os.listdir(INPUT_DIR):
        input_file = os.path.join(INPUT_DIR, input_filename)

        if zipfile.is_zipfile(input_file):
            with zipfile.ZipFile(input_file, "r") as zip_ref:
                zip_ref.extractall(INPUT_DIR)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.error(f"Error during proof generation: {e}")
        traceback.print_exc()
        sys.exit(1)
