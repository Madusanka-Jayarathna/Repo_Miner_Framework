# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
import math
from collections import defaultdict
from typing import Dict, List
from pydriller.domain.commit import Commit, ModifiedFile

from .MetricsExtractor_main import MetricsExtractor

logger = logging.getLogger(__name__)


class CodeMetricsExtractor(MetricsExtractor):
    """Extracts code/change-related metrics from commits."""

    def __init__(self, config: dict):
        super().__init__(config)

    def extract(self, commit: Commit, repo: str = None) -> Dict:
        features = {}
        modifiedFiles = commit.modified_files or []

        features['ns'] = len(set(self._getRootDir(f.filename) for f in modifiedFiles if f.filename))
        features['nd'] = len(set(self._getRootDir(f.filename) for f in modifiedFiles if f.filename))
        features['nf'] = len(modifiedFiles)

        la = sum(f.added_lines for f in modifiedFiles)
        ld = sum(f.deleted_lines for f in modifiedFiles)
        features['la'] = la
        features['ld'] = ld
        features['lt'] = la + ld

        features['entropy'] = self._calculateEntropy(modifiedFiles)
        features.update(self._extractFileTypeMetrics(modifiedFiles))
        features.update(self._extractChangeTypeMetrics(modifiedFiles))

        return features

    def _calculateEntropy(self, modifiedFiles: List[ModifiedFile]) -> float:
        if not modifiedFiles:
            return 0.0

        totalChanges = sum(f.added_lines + f.deleted_lines for f in modifiedFiles)
        if totalChanges == 0:
            return 0.0

        entropy = 0.0
        for f in modifiedFiles:
            changes = f.added_lines + f.deleted_lines
            if changes > 0:
                p = changes / totalChanges
                entropy -= p * math.log2(p)

        return entropy

    def _extractFileTypeMetrics(self, modifiedFiles: List[ModifiedFile]) -> Dict:
        features = defaultdict(int)

        for f in modifiedFiles:
            if not f.filename:
                continue
            ext = self._getExtension(f.filename)
            features[f'files_{ext}'] += 1
            features[f'la_{ext}'] += f.added_lines
            features[f'ld_{ext}'] += f.deleted_lines

        return dict(features)

    def _extractChangeTypeMetrics(self, modifiedFiles: List[ModifiedFile]) -> Dict:
        features = defaultdict(int)

        for f in modifiedFiles:
            changeType = f.change_type.name if f.change_type else 'UNKNOWN'
            features[f'change_{changeType.lower()}'] += 1

        return dict(features)