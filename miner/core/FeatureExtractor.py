# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from typing import Dict, Optional, Set
from pydriller.domain.commit import Commit

from miner.core.MetricsExtractor import (
    DeveloperMetricsExtractor,
    CodeMetricsExtractor,
    ProcessMetricsExtractor
)

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts JIT defect prediction features from commits using separate metric extractors."""

    def __init__(self, config: dict):
        self._config = config
        self._enabledMetrics = config.get('features', {})

        # Initialize metric extractors
        self._developerExtractor = DeveloperMetricsExtractor(config)
        self._codeExtractor = CodeMetricsExtractor(config)
        self._processExtractor = ProcessMetricsExtractor(config)

    def extract(self, commit: Commit, buggyCommits: Set[str], repo: str = None) -> Optional[Dict]:
        if repo is None:
            repo = getattr(commit, 'project_path', '.')

        features = {
            'commit_hash': commit.hash,
            'author': commit.author.name if commit.author else 'unknown',
            'devEmail': commit.author.email if commit.author else 'unknown',
            'commit_date': commit.committer_date.isoformat() if commit.committer_date else '',
            'is_buggy': 1 if commit.hash in buggyCommits else 0,
        }

        # Extract metrics based on configuration
        if self._enabledMetrics.get('extract_change_metrics', True):
            features.update(self._codeExtractor.extract(commit, repo))

        if self._enabledMetrics.get('extract_developer_metrics', True):
            features.update(self._developerExtractor.extract(commit, repo))

        if self._enabledMetrics.get('extract_process_metrics', False):
            features.update(self._processExtractor.extract(commit, repo))

        return features
