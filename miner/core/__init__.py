# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

"""
Metrics Extractor Package

This package provides modular metric extractors for mining software repositories.
"""

from .MetricsExtractor_main import MetricsExtractor
from .DeveloperMetricsExtractor import DeveloperMetricsExtractor
from .CodeMetricsExtractor import CodeMetricsExtractor
from .ProcessMetricExtractor import ProcessMetricExtractor

__all__ = [
    'MetricsExtractor',
    'DeveloperMetricsExtractor',
    'CodeMetricsExtractor',
    'ProcessMetricExtractor',
]

# Factory function for easy instantiation
def create_extractors(config: dict):
    """Create all metric extractors from config."""
    return {
        'developer': DeveloperMetricsExtractor(config),
        'code': CodeMetricsExtractor(config),
        'process': ProcessMetricExtractor(config),
    }# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.
