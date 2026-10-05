# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import csv
import logging
from typing import Dict, List, Optional, Set
from pydriller import Repository
from pydriller.domain.commit import Commit, ModificationType

from miner.core.BugLabeler import BugLabeler
from miner.core.FeatureExtractor import FeatureExtractor

logger = logging.getLogger(__name__)

class DataPipeline:
    """Main pipeline for JIT defect prediction feature mining."""
    
    def __init__(self, repo: str, config: dict):
        self._repo = repo
        self._config = config
        self._labeler = BugLabeler(repo, config)
        #self._extractor = FeatureExtractor(config)
        self._buggyCommits: Optional[Set[str]] = None
        logger.info("DataPipeline initialized")

    def run(self, out_file: str) -> None:
        """Execute the full pipeline and write features to CSV."""
        logger.info(f"Starting pipeline for repo: {self._repo}")
        logger.info(f"Output file: {out_file}")
        
        # Step 1: Identify buggy commits using SZZ
        logger.info("Step 1/3: Identifying buggy commits...")
        self._buggyCommits = self._labeler.getBuggyCommits()
        
        if not self._buggyCommits:
            logger.warning("No buggy commits found. Check your szz_keywords and repository.")
            return
            
        logger.info(f"Found {len(self._buggyCommits)} buggy commits")
        

    def getBuggyCommits(self) -> Set[str]:
        """Return cached buggy commits or compute if not cached."""
        if self._buggyCommits is None:
            self._buggyCommits = self._labeler.getBuggyCommits()
        return self._buggyCommits