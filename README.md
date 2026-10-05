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
    
