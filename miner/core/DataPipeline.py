# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from typing import Dict, List, Optional, Set
from pydriller import Repository
from pydriller.domain.commit import Commit, ModificationType

from miner.core.BugLabeler import BugLabeler
from miner.core.FeatureExtractor import FeatureExtractor
from miner.core.CsvReporter import CsvReporter

logger = logging.getLogger(__name__)


class DataPipeline:
    """Main pipeline for JIT defect prediction feature mining."""

    def __init__(self, repo: str, config: dict):
        self._repo = repo
        self._config = config
        self._labeler = BugLabeler(repo, config)
        self._extractor = FeatureExtractor(config)
        self._reporter = CsvReporter(config)
        self._buggyCommits: Optional[Set[str]] = None
        logger.info("DataPipeline initialized")

    def run(self, outFile: str) -> None:
        """Execute the full pipeline and write features to CSV."""
        logger.info(f"Starting pipeline for repo: {self._repo}")
        logger.info(f"Output file: {outFile}")

        # Step 1: Identify buggy commits using SZZ
        logger.info("Step 1/3: Identifying buggy commits...")
        self._buggyCommits = self._labeler.getBuggyCommits()

        if not self._buggyCommits:
            logger.warning("No buggy commits found. Check your szz_keywords and repository.")
            return

        logger.info(f"Found {len(self._buggyCommits)} buggy commits")

        # Step 2: Extract features for all commits
        logger.info("Step 2/3: Extracting features...")
        featuresData = self._getAllFeatures()

        # Step 3: Write to CSV
        logger.info("Step 3/3: Writing to CSV...")
        self._reporter.write(featuresData, outFile)

        logger.info("Pipeline completed successfully!")

    def _getAllFeatures(self) -> List[Dict]:
        """Extract features for all commits in the repository."""
        featuresList = []
        processed = 0

        # Configure Repository traversal
        repoTraversal = Repository(self._repo)

        for commit in repoTraversal.traverse_commits():
            # Skip merge commits if configured
            if self._config.get('features', {}).get('ignore_merge_commits', True):
                if commit.merge or len(commit.parents) > 1:
                    continue

            # Extract features
            features = self._extractor.extract(commit, self._buggyCommits)
            if features:
                featuresList.append(features)

            processed += 1
            if processed % 100 == 0:
                logger.debug(f"Processed {processed} commits...")

        logger.info(f"Extracted features for {len(featuresList)} commits")
        return featuresList

    def getBuggyCommits(self) -> Set[str]:
        """Return cached buggy commits or compute if not cached."""
        if self._buggyCommits is None:
            self._buggyCommits = self._labeler.getBuggyCommits()
        return self._buggyCommits