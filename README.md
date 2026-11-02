// Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
// Use of this source code is governed by the MIT license.

This Framework provides pipeline to create data sets for Research purposes
How to use:

need to add ignore dir support, ignore file considered file support for feature extraction



Methodology:
    Enhanced SZZ Algorithm
        1.Find fix commit
            search commit msg and identify bug fixing commits. 
            options : szz_keywords can be modify to enhance identification
        2.For each fix commit, get modified lines in each file
        3.Use multiple git blame to find commits that last modified those lines (-w, -C, -M)

Extracted   - E
Calculated  - C

Basic Features 
    - commitHash        - unique ID (E)
    - author            - developer (E)
    - devEmail          - developer E-mail (E)
    - commitDate        - commit date (E)
    - isBuggy           - bug or not (C) SZZ algorithm

Developer Metrics
    considering whole project
    - TotalCommits      - no of commits done (C) so far
    - TotalExp          - experience(days) since first commit to this commit (C)
    - RecentExp         - age(days) since last commit to this commit (C)
    - RecentCommits     - no of commits within last 30 days (C)
    - UniqueFileChanges - no of unique file changed up to this commit (C)
    - DevCount (ndev)   - no of unique developers edited this file (C)
    - AuthorBugCount    - no of historical bugs (C)
    - commitTime        - time in 24h format (E)
    
    considering root directory
    - SubSysCommits     - no of commits in sub system (C)
    - SubSysExp         - experience(days) since first subsystem commit to this commit (C)
    - SubSysRecentExp   - age(days) since last subsystem commit to this commit (C)

    considering leaf directory
    - libExp            - no of commits in leaf directory (C)
    - libExp      - experience(days) since first leaf level commit to this commit (C)
    - libRecentExp      - age(days) since last leaf level commit to this commit (C)



Code Metrics
    LinesAdded - no of lines added
    LinesRemoved    - no of lines deleted
    CodeChurn - LinesAdded + LinesRemoved
    NoofModifiedFiles - count of files altered in single commit
    NoofModifiedDirs - cont of directories edited in sigle commit
    Entropy - Distribution of changed code accross modified files (measuring change dispersion)

    

Process Metrics
    HighModFrequency - higest commit frequency of any of this file
    uniqueModFrequency - no of unique commits consist any of this files
    AvgModFrequency - average commits consists of any of this files

    LowChangeInterval -  days (prefered) from last change to this commit (lowest days)
    HighChangeInsterval - days (prefered) from last change to this commit (highest days)
    AvgChangeInterval - days (prefered) from last change to this commit (avg days)

    HighFileAge         - days (prefered) from file created to this commit (highest)
    LowFileAge         - days (prefered) from file created to this commit (lowest)
    AgFileAge         - days (prefered) from file created to this commit (avg)


    HighDefectCounts   - highest defects previous defect count of any of file (highest)
    LowDefectCounts   - highest defects previous defect count of any of file (lowest)
    AvgDefectCounts   - highest defects previous defect count of any of file (average)
    TotUniqueDefectHistory - no of unique defect consist any of this file (Total)

    IsBugFixingCommit    - intension is bug fixe (1) or not (0)
