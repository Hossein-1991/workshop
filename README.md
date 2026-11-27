# Survey Cleaning Pipeline

A small T project for the Section 4.5 pair/trio exercise. The pipeline reads
data/survey.csv, drops rows without a respondent ID, normalizes group labels,
marks negative sentinel scores as missing, and computes sample-standardized
scores in a pure Python function.

## Golden result

After cleaning, the four retained respondents have scores 10, 20, 30, and
missing. The valid-score sample mean is 20 and sample standard deviation
(ddof=1) is 10, so the expected score_z values are -1, 0, 1, and missing.
The row with no respondent ID is excluded.

## Run

Enter the Nix environment, then run:

    t run src/pipeline.t
    pytest
    t test --json

The unit tests compare against the hand-calculated table and cover invalid
inputs, empty data, constant and missing scores, invariants, and immutability.
The Testcraft test checks pipeline structure and built node output.
