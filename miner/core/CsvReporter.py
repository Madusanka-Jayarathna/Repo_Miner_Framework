# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.

import csv
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CsvReporter:
    """Handles CSV report generation for extracted features."""

    def __init__(self, config: dict = None):
        self._config = config or {}

    def write(self, featuresData: List[Dict], outFile: str) -> None:
        """Write features to CSV file."""
        if not featuresData:
            logger.warning("No features to write")
            return

        # Get all possible field names (union of all keys)
        fieldNames = set()
        for row in featuresData:
            fieldNames.update(row.keys())
        fieldNames = sorted(fieldNames)

        # Ensure label column is first
        if 'is_buggy' in fieldNames:
            fieldNames.remove('is_buggy')
            fieldNames = ['is_buggy'] + fieldNames

        with open(outFile, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(featuresData)

        logger.info(f"Written {len(featuresData)} rows to {outFile}")