# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from pydriller.domain.commit import Commit

from .MetricsExtractor_main import MetricsExtractor

logger = logging.getLogger(__name__)


class ProcessMetricExtractor(MetricsExtractor):
    """Extracts process-related metrics from commits (e.g., time-based, workflow metrics)."""

    def __init__(self, config: dict):
        super().__init__(config)
        procConfig = config.get('process_metrics', {})
        self._timeWindowDays = procConfig.get('timeWindowDays', 30)

        # Process-level tracking
        self._commitDates: List[datetime] = []
        self._commitHours: List[int] = []
        self._commitDaysOfWeek: List[int] = []
        self._authorCommitCounts: Dict[str, int] = defaultdict(int)
        self._fileCommitCounts: Dict[str, int] = defaultdict(int)
        self._subsystemCommitCounts: Dict[str, int] = defaultdict(int)
        self._bugFixCommitCount: int = 0
        self._totalCommits: int = 0

    def extract(self, commit: Commit, repo: str = None) -> Dict:
        commitDate = self._getCommitDate(commit)
        commitHour = self._getCommitHour(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)
        isBugFix = self._isBugFixCommit(commit)
        devEmail = self._getDevEmail(commit)

        features = {}

        # Time since last commit (process pace)
        timeSinceLastCommit = 0
        if self._commitDates and commitDate is not None:
            lastCommitDate = max(self._commitDates)
            timeSinceLastCommit = (commitDate - lastCommitDate).total_seconds() / 3600  # hours

        features['timeSinceLastCommit'] = timeSinceLastCommit

        # Commits in last time window
        recentCommits = 0
        if commitDate is not None:
            cutoffDate = commitDate - timedelta(days=self._timeWindowDays)
            recentCommits = sum(1 for d in self._commitDates if d >= cutoffDate)
        features['recentCommits'] = recentCommits

        # Commit hour (0-23)
        features['commitHour'] = commitHour

        # Day of week (0=Monday, 6=Sunday)
        dayOfWeek = -1
        if commitDate is not None:
            dayOfWeek = commitDate.weekday()
        features['commitDayOfWeek'] = dayOfWeek

        # Is weekend commit
        features['isWeekend'] = 1 if dayOfWeek >= 5 else 0

        # Is late night commit (22:00 - 06:00)
        features['isLateNight'] = 1 if (commitHour >= 22 or commitHour <= 6) else 0

        # Total commits so far
        features['totalCommitsSoFar'] = self._totalCommits

        # Bug fix ratio so far
        bugFixRatio = 0
        if self._totalCommits > 0:
            bugFixRatio = self._bugFixCommitCount / self._totalCommits
        features['bugFixRatio'] = bugFixRatio

        # Author commit count so far
        features['authorCommitCount'] = self._authorCommitCounts.get(devEmail, 0)

        # File commit counts (average, max)
        fileCommitCounts = [self._fileCommitCounts.get(f, 0) for f in files]
        features['avgFileCommitCount'] = sum(fileCommitCounts) / len(fileCommitCounts) if fileCommitCounts else 0
        features['maxFileCommitCount'] = max(fileCommitCounts) if fileCommitCounts else 0

        # Subsystem commit counts
        subsystemCommitCounts = [self._subsystemCommitCounts.get(s, 0) for s in subsystems]
        features['avgSubsystemCommitCount'] = sum(subsystemCommitCounts) / len(subsystemCommitCounts) if subsystemCommitCounts else 0
        features['maxSubsystemCommitCount'] = max(subsystemCommitCounts) if subsystemCommitCounts else 0

        # Number of subsystems touched
        features['numSubsystemsTouched'] = len(subsystems)

        # Number of files touched
        features['numFilesTouched'] = len(files)

        return features

    def update(self, commit: Commit, isBuggy: Optional[bool] = None) -> None:
        commitDate = self._getCommitDate(commit)
        commitHour = self._getCommitHour(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)
        isBugFix = self._isBugFixCommit(commit)
        devEmail = self._getDevEmail(commit)

        if commitDate is not None:
            self._commitDates.append(commitDate)
            self._commitHours.append(commitHour)
            self._commitDaysOfWeek.append(commitDate.weekday())

        self._totalCommits += 1
        self._authorCommitCounts[devEmail] += 1

        if isBugFix:
            self._bugFixCommitCount += 1

        for filename in files:
            self._fileCommitCounts[filename] += 1

        for subsystem in subsystems:
            self._subsystemCommitCounts[subsystem] += 1

    def reset(self) -> None:
        self._commitDates = []
        self._commitHours = []
        self._commitDaysOfWeek = []
        self._authorCommitCounts = defaultdict(int)
        self._fileCommitCounts = defaultdict(int)
        self._subsystemCommitCounts = defaultdict(int)
        self._bugFixCommitCount = 0
        self._totalCommits = 0