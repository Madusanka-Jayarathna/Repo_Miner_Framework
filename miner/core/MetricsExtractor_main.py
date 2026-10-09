# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from pydriller.domain.commit import Commit
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

    def update(self, commit: Commit, isBuggy: Optional[bool] = None) -> None:
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

    def _getLeafDir(self, filepath: str) -> str:
            """
            Extracts the directory path containing the file.
            If the immediate parent directory is 'private' or 'public', it truncates
            up to the immediate parent directory before 'private'/'public'.
            """
            if not filepath:
                return 'root'
            
            # Normalize leading/trailing slashes
            cleanPath = filepath.strip('/')
            parts = cleanPath.split('/')
            
            # File is at repo root
            if len(parts) <= 1:
                return 'root'
                
            # Extract folder hierarchy (excluding filename)
            dirParts = parts[:-1]
            
            # If the last directory is 'private' or 'public', step up one level
            if dirParts[-1].lower() in ('private', 'public'):
                dirParts = dirParts[:-1]
                
            if not dirParts:
                return 'root'
                
            return '/'.join(dirParts)

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

    def _getCommitHour(self, commit: Commit) -> int:
        """Get commit hour in 24h format (0-23)."""
        commitDate = self._getCommitDate(commit)
        if commitDate is not None:
            return commitDate.hour
        return -1

    def _isBugFixCommit(self, commit: Commit) -> bool:
        """Detect if commit is a bug fix based on commit message."""
        if not commit.msg:
            return False
        msg = commit.msg.lower()
        bug_keywords = ['fix', 'bug', 'defect', 'issue', 'error', 'crash', 'patch', 'hotfix']
        return any(keyword in msg for keyword in bug_keywords)