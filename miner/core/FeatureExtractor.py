# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from typing import Dict, Optional, Set
from pydriller.domain.commit import Commit

from .DeveloperMetricsExtractor import DeveloperMetricsExtractor
from .CodeMetricsExtractor import CodeMetricsExtractor
from .ProcessMetricExtractor import ProcessMetricExtractor

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts JIT defect prediction features from commits using separate metric extractors."""

    def __init__(self, config: dict):
        self._config = config
        self._enabledMetrics = config.get('features', {})

        # Initialize metric extractors
        self._developerExtractor = DeveloperMetricsExtractor(config)
        self._codeExtractor = CodeMetricsExtractor(config)
        self._processExtractor = ProcessMetricExtractor(config)

    def extract(self, commit: Commit, buggyCommits: Set[str], repo: str = None) -> Optional[Dict]:
        if repo is None:
            repo = getattr(commit, 'project_path', '.')

        isBuggy = 1 if commit.hash in buggyCommits else 0
        features = {
            'commitHash': commit.hash,
            'author': commit.author.name if commit.author else 'unknown',
            'devEmail': commit.author.email if commit.author else 'unknown',
            'commitDate': commit.committer_date.isoformat() if commit.committer_date else '',
            'isBuggy': isBuggy,
        }

        # Extract metrics based on configuration
        if self._enabledMetrics.get('extract_change_metrics', True):
            features.update(self._codeExtractor.extract(commit, repo))
            #self._codeExtractor.update(commit, isBuggy)  

        if self._enabledMetrics.get('extract_developer_metrics', True):
            features.update(self._developerExtractor.extract(commit, repo))
            self._developerExtractor.update(commit, isBuggy)

        if self._enabledMetrics.get('extract_process_metrics', False):
            features.update(self._processExtractor.extract(commit, repo))
            #self._processExtractor.update(commit, isBuggy)

        return features
