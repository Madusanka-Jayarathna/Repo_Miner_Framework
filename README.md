// Copyright (c) 2026 Madusanka Jayarathna. All rights reserved.
// Use of this source code is governed by the MIT license.

This Framework provides pipeline to create data sets for Research purposes
How to use:



Methodology:
    Enhanced SZZ Algorithm
        1.Find fix commit
            search commit msg and identify bug fixing commits. 
            options : szz_keywords can be modify to enhance identification
        2.For each fix commit, get modified lines in each file
        3.Use multiple git blame to find commits that last modified those lines (-w, -C, -M)

Developer Metrics
    TotalCommits - no of commits done
    TotalExp    - days(prefered) from first commit to this commit
    RecentExp   - days(prefered) from last commit to this commit
    RecentCommits - commits within last 30 days
    UniqueFileChanges - no of unique file changed up to this commit
    
    SubSysCommits - no of commits in sub system
    SubSysExp   - days (prefered) from first subsystem commit to this commit
    SubSysRecentExp - days (prefered) from last subsystem commit to this commit

    DevCount    - no of unique developers edited this file
    HistoricBugCount - no of historical bugs

    commitTime  - time in 24h format (late night bugs)

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
