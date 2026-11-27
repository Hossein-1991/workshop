-- intent {
-- assumptions: the survey fixture contains one missing ID and one negative sentinel score.
-- goals: verify the pipeline DAG, Arrow IPC contract, and cleaned output.
-- dependencies: data/survey.csv; src/cleaning.py; Testcraft expectations.
-- }
survey_test_pipeline = pipeline {
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

assert(expect_pipeline(survey_test_pipeline))
assert(expect_nodes(survey_test_pipeline, ["raw_survey", "cleaned_survey", "flagged_survey"]))
assert(expect_dependency(survey_test_pipeline, "raw_survey", "cleaned_survey"))
assert(expect_dependency(survey_test_pipeline, "cleaned_survey", "flagged_survey"))
assert(expect_serializer(survey_test_pipeline, "cleaned_survey", ^ipc))
assert(expect_serializer(survey_test_pipeline, "flagged_survey", ^ipc))

build_pipeline(survey_test_pipeline)

cleaned = read_node(survey_test_pipeline.cleaned_survey)
assert(expect_nrow(cleaned, 4))
assert(expect_no_na(cleaned, "respondent_id"))
assert(expect_has_colnames(cleaned, ["respondent_id", "group", "score", "score_z"]))

flagged = read_node(survey_test_pipeline.flagged_survey)
assert(expect_nrow(flagged, 4))
assert(expect_has_colnames(flagged, ["respondent_id", "group", "score", "score_z", "is_outlier"]))
