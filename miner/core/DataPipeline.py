# Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
# Use of this source code is governed by the MIT license.


class DataPipeline:
    def __init__(self, repo, config):
        self.repo = repo
        self.config = config
        print("initialization of DataPipeline class done!")

    def run(self, outFile):
        print(f"outFileName:{outFile}")