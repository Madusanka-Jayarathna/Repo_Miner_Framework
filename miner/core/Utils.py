# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import re

from pydriller.domain.commit import Commit

_BOT_PATTERNS = (
    r'\[bot\]', r'bot@', r'^bot$', r'github-actions', r'gitlab-bot',
    r'dependabot', r'renovate', r'greenkeeper', r'codecov', r'snyk',
    r'sonarcloud', r'semantic-release', r'stale', r'mergify',
    r'crowdin', r'imgbot', r'deepsource', r'deepsource-autofix'
)
_BOT_REGEX = re.compile('|'.join(_BOT_PATTERNS), re.IGNORECASE)


def isBotCommit(commit: Commit) -> bool:
    """Return whether the commit was authored by a recognized bot."""
    author_email = commit.author.email.lower() if commit.author.email else ''
    author_name = commit.author.name.lower() if commit.author.name else ''
    return bool(_BOT_REGEX.search(author_email) or _BOT_REGEX.search(author_name))
