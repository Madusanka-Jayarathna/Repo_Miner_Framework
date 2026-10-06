# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
import math
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set
from pydriller.domain.commit import Commit, ModifiedFile
from pydriller import Git

logger = logging.getLogger(__name__)


class MetricsExtractor(ABC):
    """Base class for all metrics extractors. Enables expandability for new metric types."""

    def __init__(self, config: dict):
        self._config = config
        self._git = None

    @abstractmethod
    def extract(self, commit: Commit, repo: str = None) -> Dict:
        """Extract metrics for a given commit using only history seen so far (no future leakage)."""
        pass

    def update(self, commit: Commit) -> None:
        """Record a processed commit into history. Default is stateless (no-op)."""
        return None

    def reset(self) -> None:
        """Clear accumulated history. Default is stateless (no-op)."""
        return None

    def _getGit(self, repo: str) -> Git:
        if self._git is None:
            self._git = Git(repo)
        return self._git

    def _getRootDir(self, filepath: str) -> str:
        if not filepath:
            return 'root'
        parts = filepath.split('/')
        return parts[0] if len(parts) > 1 else 'root'

    def _getExtension(self, filename: str) -> str:
        if '.' not in filename:
            return 'noext'
        return filename.split('.')[-1].lower()

    def _getDevEmail(self, commit: Commit) -> str:
        if commit.author and commit.author.email:
            return commit.author.email.strip().lower()
        if commit.author and commit.author.name:
            return commit.author.name.strip().lower()
        return 'unknown'

    def _getCommitDate(self, commit: Commit) -> Optional[datetime]:
        return commit.committer_date or commit.author_date

    def _getCommitFiles(self, commit: Commit) -> List[str]:
        files = []
        for f in commit.modified_files or []:
            filename = f.new_path or f.old_path or f.filename
            if filename:
                files.append(filename)
        return files


class DeveloperMetricsExtractor(MetricsExtractor):
    """Extracts developer-related metrics from commits using incremental history."""

    def __init__(self, config: dict):
        super().__init__(config)
        devConfig = config.get('developer_metrics', {})
        self._recentDays = devConfig.get('recentDays', 90)
        self._authorDates: Dict[str, List[datetime]] = defaultdict(list)
        self._authorFirstSeen: Dict[str, datetime] = {}
        self._authorFiles: Dict[str, Set[str]] = defaultdict(set)
        self._authorSubsystems: Dict[str, Set[str]] = defaultdict(set)
        self._subsystemAuthors: Dict[str, Set[str]] = defaultdict(set)
        self._fileAuthors: Dict[str, Set[str]] = defaultdict(set)

    def extract(self, commit: Commit, repo: str = None) -> Dict:
        devEmail = self._getDevEmail(commit)
        commitDate = self._getCommitDate(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)

        priorDates = self._authorDates.get(devEmail, [])
        exp = len(priorDates)

        if commitDate is not None:
            rexp = sum(1 for d in priorDates if d is not None and 0 <= (commitDate - d).days <= self._recentDays)
        else:
            rexp = exp

        sexp = 0
        for subsystem in subsystems:
            authors = self._subsystemAuthors.get(subsystem, set())
            sexp += sum(1 for d in priorDates if devEmail in authors)

        otherDevs: Set[str] = set()
        for filename in files:
            otherDevs.update(self._fileAuthors.get(filename, set()))
        otherDevs.discard(devEmail)
        ndev = len(otherDevs)

        age = 0
        firstSeen = self._authorFirstSeen.get(devEmail)
        if firstSeen is not None and commitDate is not None:
            age = max(0, (commitDate - firstSeen).days)

        nuc = len(self._authorFiles.get(devEmail, set()))

        return {
            'exp': exp,
            'rexp': rexp,
            'sexp': sexp,
            'ndev': ndev,
            'age': age,
            'nuc': nuc,
        }

    def update(self, commit: Commit) -> None:
        devEmail = self._getDevEmail(commit)
        commitDate = self._getCommitDate(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)

        if commitDate is not None:
            self._authorDates[devEmail].append(commitDate)
            if devEmail not in self._authorFirstSeen:
                self._authorFirstSeen[devEmail] = commitDate
            elif commitDate < self._authorFirstSeen[devEmail]:
                self._authorFirstSeen[devEmail] = commitDate

        for filename in files:
            self._authorFiles[devEmail].add(filename)
            self._fileAuthors[filename].add(devEmail)

        for subsystem in subsystems:
            self._authorSubsystems[devEmail].add(subsystem)
            self._subsystemAuthors[subsystem].add(devEmail)

    def reset(self) -> None:
        self._authorDates = defaultdict(list)
        self._authorFirstSeen = {}
        self._authorFiles = defaultdict(set)
        self._authorSubsystems = defaultdict(set)
        self._subsystemAuthors = defaultdict(set)
        self._fileAuthors = defaultdict(set)


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
