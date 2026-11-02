# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import argparse
import logging
import os
import sys
import yaml

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from miner.core.DataPipeline import DataPipeline  


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("repo_miner.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger("pydriller.repository").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Defect Prediction Feature Mining Framework")
    #parser.add_argument("-v", "--") add support for perforce later
    parser.add_argument("-r", "--repo", required=True, help="Path to Git repository")
    parser.add_argument("-o", "--output", default="extracted_features.csv", help="Output CSV path")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to YAML configuration file")    

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        parser.error(f"configuration file not found: {args.config}")

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    pipeline = DataPipeline(repo=args.repo, config=config)
    pipeline.run(outFile=args.output)


if __name__ == "__main__":
    main()