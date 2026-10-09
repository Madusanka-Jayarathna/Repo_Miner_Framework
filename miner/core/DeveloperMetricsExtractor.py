# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from pydriller.domain.commit import Commit

from .MetricsExtractor_main import MetricsExtractor

logger = logging.getLogger(__name__)


class DeveloperMetricsExtractor(MetricsExtractor):
    """Extracts developer-related metrics from commits using incremental history."""

    def __init__(self, config: dict):
        super().__init__(config)
        devConfig = config.get('developer_metrics', {})
        self._recentCommitsDays = devConfig.get('recentCommitsDays', 30)

        # Developer-level tracking
        self._authorDates: Dict[str, List[datetime]] = defaultdict(list)
        self._authorFirstSeen: Dict[str, datetime] = {}
        self._authorLastSeen: Dict[str, datetime] = {}
        self._authorFiles: Dict[str, Set[str]] = defaultdict(set)
        self._authorSubsystems: Dict[str, Set[str]] = defaultdict(set)
        self._authorSubsystemDates: Dict[str, Dict[str, List[datetime]]] = defaultdict(lambda: defaultdict(list))
        self._authorSubsystemFirstSeen: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        self._authorSubsystemLastSeen: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        self._authorTotalCommits: Dict[str, int] = defaultdict(int)
        self._authorRecentCommits: Dict[str, List[datetime]] = defaultdict(list)
        self._authorBuggyCommits: Dict[str, int] = defaultdict(int)

        # Library-level tracking (Developer x Library directory)
        self._authorLibraries: Dict[str, Set[str]] = defaultdict(set)
        self._authorLibraryDates: Dict[str, Dict[str, List[datetime]]] = defaultdict(lambda: defaultdict(list))
        self._authorLibraryFirstSeen: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        self._authorLibraryLastSeen: Dict[str, Dict[str, datetime]] = defaultdict(dict)

        # File-level tracking
        self._fileAuthors: Dict[str, Set[str]] = defaultdict(set)
        #self._fileBugFixCount: Dict[str, int] = defaultdict(int)

        # Subsystem-level tracking
        self._subsystemAuthors: Dict[str, Set[str]] = defaultdict(set)
        self._subsystemCommits: Dict[str, int] = defaultdict(int)
        self._subsystemDates: Dict[str, List[datetime]] = defaultdict(list)
        self._subsystemFirstSeen: Dict[str, datetime] = {}
        self._subsystemLastSeen: Dict[str, datetime] = {}

    
    def extract(self, commit: Commit, repo: str = None) -> Dict:
        devEmail = self._getDevEmail(commit)
        commitDate = self._getCommitDate(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)
        libraries = set(self._getLeafDir(f) for f in files)
        commitHour = self._getCommitHour(commit)
        #isBugFix = self._isBugFixCommit(commit)

        # Get prior history for this developer
        priorDates = self._authorDates.get(devEmail, [])
        priorDatesSorted = sorted([d for d in priorDates if d is not None])

        # TotalCommits - total number of commits done by this developer before this commit
        totalCommits = self._authorTotalCommits.get(devEmail, 0)

        # TotalExp - days from first commit to this commit
        totalExp = 0
        firstSeen = self._authorFirstSeen.get(devEmail)
        if firstSeen is not None and commitDate is not None:
            totalExp = max(0, (commitDate - firstSeen).days)

        # RecentExp - days from last commit to this commit
        recentExp = 0
        lastSeen = self._authorLastSeen.get(devEmail)
        if lastSeen is not None and commitDate is not None:
            recentExp = max(0, (commitDate - lastSeen).days)

        # RecentCommits - commits within last 30 days (configurable)
        recentCommits = 0
        if commitDate is not None:
            cutoffDate = commitDate - timedelta(days=self._recentCommitsDays)
            recentCommits = sum(1 for d in priorDatesSorted if d >= cutoffDate)

        # UniqueFileChanges - no of unique files changed up to this commit
        uniqueFileChanges = len(self._authorFiles.get(devEmail, set()))

        # SubSysCommits - no of commits in subsystem(s) for this developer
        subSysCommits = 0
        for subsystem in subsystems:
            subSysCommits += len(self._authorSubsystemDates.get(devEmail, {}).get(subsystem, []))

        # SubSysExp - days from first subsystem commit to this commit
        subSysExp = 0
        for subsystem in subsystems:
            firstSubSysSeen = self._authorSubsystemFirstSeen.get(devEmail, {}).get(subsystem)
            if firstSubSysSeen is not None and commitDate is not None:
                days = (commitDate - firstSubSysSeen).days
                if days > subSysExp:
                    subSysExp = max(0, days)

        # SubSysRecentExp - days from last subsystem commit to this commit
        subSysRecentExp = 0
        for subsystem in subsystems:
            lastSubSysSeen = self._authorSubsystemLastSeen.get(devEmail, {}).get(subsystem)
            if lastSubSysSeen is not None and commitDate is not None:
                days = (commitDate - lastSubSysSeen).days
                if days > subSysRecentExp:
                    subSysRecentExp = max(0, days)

        # 3. Library-level metrics
        libCommits = 0
        for lib in libraries:
            libCommits += len(self._authorLibraryDates.get(devEmail, {}).get(lib, []))

        libExp = 0
        for lib in libraries:
            firstLibSeen = self._authorLibraryFirstSeen.get(devEmail, {}).get(lib)
            if firstLibSeen is not None and commitDate is not None:
                days = (commitDate - firstLibSeen).days
                if days > libExp:
                    libExp = max(0, days)

        libRecentExp = 0
        for lib in libraries:
            lastLibSeen = self._authorLibraryLastSeen.get(devEmail, {}).get(lib)
            if lastLibSeen is not None and commitDate is not None:
                days = (commitDate - lastLibSeen).days
                if days > libRecentExp:
                    libRecentExp = max(0, days)

        # DevCount - no of unique developers edited this file (across all files in commit)
        devCount = 0
        allDevs: Set[str] = set()
        for filename in files:
            allDevs.update(self._fileAuthors.get(filename, set()))
        allDevs.discard(devEmail)
        devCount = len(allDevs)

        authorBugCount = self._authorBuggyCommits.get(devEmail, 0)

        #historicBugCount = sum(self._fileBugFixCount.get(filename, 0) for filename in files)
        commitTime = commitHour

        return {
            # New metrics
            'TotalCommits': totalCommits,
            'TotalExp': totalExp,
            'RecentExp': recentExp,
            'RecentCommits': recentCommits,
            'UniqueFileChanges': uniqueFileChanges,
            'SubSysCommits': subSysCommits,
            'SubSysExp': subSysExp,
            'SubSysRecentExp': subSysRecentExp,
            'libCommits': libCommits,
            'libExp': libExp,
            'libRecentExp': libRecentExp,
            'DevCount': devCount,
            'AuthorBugCount': authorBugCount,
            'commitTime': commitTime
        }

    def update(self, commit: Commit, isBuggy: Optional[bool] = None) -> None:
        devEmail = self._getDevEmail(commit)
        commitDate = self._getCommitDate(commit)
        files = self._getCommitFiles(commit)
        subsystems = set(self._getRootDir(f) for f in files)
        libraries = set(self._getLeafDir(f) for f in files)

        if commitDate is not None:
            # Update developer commit history
            self._authorDates[devEmail].append(commitDate)
            self._authorTotalCommits[devEmail] += 1

            # Track first and last seen
            if devEmail not in self._authorFirstSeen:
                self._authorFirstSeen[devEmail] = commitDate
            elif commitDate < self._authorFirstSeen[devEmail]:
                self._authorFirstSeen[devEmail] = commitDate

            self._authorLastSeen[devEmail] = commitDate

            # Track recent commits (for RecentCommits metric)
            self._authorRecentCommits[devEmail].append(commitDate)

            # Track bug fix commits
            if isBuggy:
                self._authorBuggyCommits[devEmail] += 1

        # Update file-level tracking
        for filename in files:
            self._authorFiles[devEmail].add(filename)
            self._fileAuthors[filename].add(devEmail)
            if isBuggy:
                self._fileBuggyCount[filename] += 1

        # Update subsystem-level tracking
        for subsystem in subsystems:
            self._authorSubsystems[devEmail].add(subsystem)
            self._subsystemAuthors[subsystem].add(devEmail)
            self._subsystemCommits[subsystem] += 1

            if commitDate is not None:
                self._authorSubsystemDates[devEmail][subsystem].append(commitDate)
                self._subsystemDates[subsystem].append(commitDate)

                # Track first/last seen for subsystem per developer
                if subsystem not in self._authorSubsystemFirstSeen[devEmail]:
                    self._authorSubsystemFirstSeen[devEmail][subsystem] = commitDate
                elif commitDate < self._authorSubsystemFirstSeen[devEmail][subsystem]:
                    self._authorSubsystemFirstSeen[devEmail][subsystem] = commitDate

                self._authorSubsystemLastSeen[devEmail][subsystem] = commitDate

                # Track first/last seen for subsystem globally
                if subsystem not in self._subsystemFirstSeen:
                    self._subsystemFirstSeen[subsystem] = commitDate
                elif commitDate < self._subsystemFirstSeen[subsystem]:
                    self._subsystemFirstSeen[subsystem] = commitDate

                self._subsystemLastSeen[subsystem] = commitDate

        # Update Library-level tracking
        for lib in libraries:
            self._authorLibraries[devEmail].add(lib)

            if commitDate is not None:
                self._authorLibraryDates[devEmail][lib].append(commitDate)

                if lib not in self._authorLibraryFirstSeen[devEmail]:
                    self._authorLibraryFirstSeen[devEmail][lib] = commitDate
                elif commitDate < self._authorLibraryFirstSeen[devEmail][lib]:
                    self._authorLibraryFirstSeen[devEmail][lib] = commitDate

                self._authorLibraryLastSeen[devEmail][lib] = commitDate

    def reset(self) -> None:
        self._authorDates = defaultdict(list)
        self._authorFirstSeen = {}
        self._authorLastSeen = {}
        self._authorFiles = defaultdict(set)
        self._authorSubsystems = defaultdict(set)
        self._authorSubsystemDates = defaultdict(lambda: defaultdict(list))
        self._authorSubsystemFirstSeen = defaultdict(dict)
        self._authorSubsystemLastSeen = defaultdict(dict)
        self._authorTotalCommits = defaultdict(int)
        self._authorRecentCommits = defaultdict(list)
        self._authorBugFixCommits = defaultdict(int)

        self._authorLibraries = defaultdict(set)
        self._authorLibraryDates = defaultdict(lambda: defaultdict(list))
        self._authorLibraryFirstSeen = defaultdict(dict)
        self._authorLibraryLastSeen = defaultdict(dict)

        self._fileAuthors = defaultdict(set)
        self._fileBugFixCount = defaultdict(int)
        self._subsystemAuthors = defaultdict(set)
        self._subsystemCommits = defaultdict(int)
        self._subsystemDates = defaultdict(list)
        self._subsystemFirstSeen = {}
        self._subsystemLastSeen = {}
