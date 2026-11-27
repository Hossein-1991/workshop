-- intent {
-- assumptions: blank respondent IDs are missing, and negative scores are sentinels.
-- goals: ingest survey data, clean/standardize scores, and flag outliers reproducibly.
-- dependencies: data/survey.csv; src/cleaning.py; pandas; numpy; pyarrow.
-- }
p = pipeline {
  raw_survey = node(
    command = read_csv("data/survey.csv"),
    serializer = ^ipc
  )

  cleaned_survey = pyn(
    command = <{ clean_survey_scores(raw_survey) }>,
    functions = ["src/cleaning.py"],
    deserializer = ^ipc,
    serializer = ^ipc
  )

  flagged_survey = pyn(
    command = <{ flag_outliers(cleaned_survey) }>,
    functions = ["src/cleaning.py"],
    deserializer = ^ipc,
    serializer = ^ipc
  )
}

build_pipeline(p)
