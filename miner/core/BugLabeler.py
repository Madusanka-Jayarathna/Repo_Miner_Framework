# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import re
import logging
from typing import Set, List, Optional
from pydriller import Repository, Git
from pydriller.domain.commit import Commit

logger = logging.getLogger(__name__)


class BugLabeler:
    """Identifies bug-fixing commits and traces back to bug-introducing commits using SZZ algorithm."""

    def __init__(self, repo: str, config: dict):
        self._repo = repo
        self._config = config
        self._git = Git(self._repo)

        # process configurations
        self._patterns = self._getNormalizePattern()
        self._fileExtensions = tuple(config.get('file_type', []))
        self._ignoreDirs = tuple(config.get('exclude_dirs', []))

        self._ignoreMergeCommit = config.get('features', {}).get('ignore_merge_commits', True)
        self._ignoreBotCommit = config.get('features', {}).get('ignore_bot_commits', True)

        self._botPatterns = [
            r'\[bot\]', r'bot@', r'github-actions', r'gitlab-bot',
            r'dependabot', r'renovate', r'greenkeeper', r'codecov'
        ]
        self._botRegex = re.compile('|'.join(self._botPatterns), re.IGNORECASE)


    def _getNormalizePattern(self) -> re.Pattern:
        """Compile case-insensitive regex pattern from szz_keywords."""
        keywords = self._config.get('szz_keywords', [])
        if not keywords:
            logger.warning("No szz_keywords configured, using default patterns")
            keywords = ['fix', 'bug', 'issue', 'patch', 'resolve', 'close']

        # Escape keywords and join with word boundaries
        escaped = [re.escape(kw) for kw in keywords]
        pattern = r'\b(?:' + '|'.join(escaped) + r')\b'
        return re.compile(pattern, re.IGNORECASE)


    def _isProcessableFile(self, filename: Optional[str]) -> bool:
        """Check if file should be processed based on extension and exclude dirs."""
        if not filename:
            return False

        # Check file extension
        if self._fileExtensions and not filename.endswith(self._fileExtensions):
            return False

        # Check exclude directories
        if self._ignoreDirs and any(filename.startswith(d) for d in self._ignoreDirs):
            return False

        return True


    def _isMergeCommit(self, commit: Commit) -> bool:
        """Check if commit is a merge commit."""
        return commit.merge or len(commit.parents) > 1


    def _isBotCommit(self, commit: Commit) -> bool:
        """Check if commit is from a bot."""
        authorEmail = commit.author.email.lower() if commit.author.email else ''
        authorName = commit.author.name.lower() if commit.author.name else ''
        return bool(self._botRegex.search(authorEmail) or self._botRegex.search(authorName))


    def _isFixCommit(self, commit: Commit) -> bool:
        """Check if commit message indicates a bug fix."""
        if not commit.msg:
            return False
        return bool(self._patterns.search(commit.msg))


    def _getFixCommits(self) -> List[Commit]:
        """Get all commits that are identified as bug fixes."""
        fixCommits = []

        for commit in Repository(self._repo).traverse_commits():
            if self._ignoreMergeCommit and self._isMergeCommit(commit):
                continue

            if self._ignoreBotCommit and self._isBotCommit(commit):
                continue

            if self._isFixCommit(commit):
                fixCommits.append(commit)

        logger.info(f"Found {len(fixCommits)} fix commits")
        return fixCommits


    def getBuggyCommits(self) -> Set[str]:
        """
        Implement SZZ algorithm:
        1. Find fix commits
        2. For each fix commit, get modified lines in each file
        3. Use git blame to find commits that last modified those lines
        4. Those commits are the bug-introducing commits
        """
        buggyCommits = set()
        fixCommits = self._getFixCommits()

        for fixCommit in fixCommits:
            for modifiedFile in fixCommit.modified_files:
                if not self._isProcessableFile(modifiedFile.filename):
                    continue

                try:
                    # Get lines that were deleted/modified in the fix (these are the buggy lines)
                    # PyDriller's get_commits_last_modified_lines returns a dict mapping
                    # file path to set of commit hashes that last modified those lines
                    blameResult = self._git.get_commits_last_modified_lines(fixCommit, modifiedFile)

                    if blameResult:
                        for filePath, commitHashes in blameResult.items():
                            if self._isProcessableFile(filePath):
                                buggyCommits.update(commitHashes)

                except Exception as e:
                    logger.warning(
                        f"Failed to process blame for {modifiedFile.filename} "
                        f"in commit {fixCommit.hash[:8]}: {e}"
                    )
                    continue

        logger.info(f"Identified {len(buggyCommits)} bug-introducing commits")
        return buggyCommits