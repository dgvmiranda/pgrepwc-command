# Parallel Grep with Counting (pgrepwc)

## OBJECTIVES
The objective of this project is to develop a Python program that involves creating processes/threads and enabling communication between them. Specifically, the task is to create a command-line tool, pgrepwc, which searches for a specified word in one or more files, outputs the lines containing the word, and provides counts of the occurrences and lines found.

## INTRODUCTION
The traditional grep command searches lines in files containing a specific word or regular expression. However, grep can have performance issues when dealing with multiple files and multiple search terms. The goal of this project is to develop pgrepwc (parallel grep with counting), an enhanced version of grep that parallelizes the search process and provides additional functionalities.

## SINOPSE
./pgrepwc [-c] [-l] [-p n] [-t] [-e] word {files}

## DESCRIPTION
**-c:** Option to count the total number of isolated occurrences of the search word.

**-l:** Option to count the total number of lines containing one or more occurrences of the search word.

**-p n:** Option to define the level of parallelization n (number of processes/threads to use for the search and counting). By default, only one process (the parent process) is used.

**-e k:** The parameter k defines the maximum number of bytes that make up a work block.

**word:** The word to search for in the content of the file(s).

**files:** One or more files to search. If no files are specified, the files will be read from stdin (the command will prompt the user for the files to process).
