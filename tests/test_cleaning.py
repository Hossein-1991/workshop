import numpy as np
import pandas as pd
import pytest

from src.cleaning import clean_survey_scores, flag_outliers


def golden_input():
    return pd.DataFrame(
        {
            "respondent_id": [101, 102, 103, None, 104],
            "group": [" Alpha ", "BETA", " alpha", "Gamma", "Gamma"],
            "score": [10, 20, 30, 40, -999],
        }
    )


def test_happy_path_matches_hand_calculated_golden_table():
    actual = clean_survey_scores(golden_input())
    expected = pd.DataFrame(
        {
            "respondent_id": [101.0, 102.0, 103.0, 104.0],
            "group": ["alpha", "beta", "alpha", "gamma"],
            "score": [10.0, 20.0, 30.0, np.nan],
            "score_z": [-1.0, 0.0, 1.0, np.nan],
        }
    )
    pd.testing.assert_frame_equal(
        actual.reset_index(drop=True),
        expected,
        check_dtype=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_missing_required_columns_raise_informative_error():
    with pytest.raises(ValueError, match="missing required columns: score"):
        clean_survey_scores(pd.DataFrame({"respondent_id": [1], "group": ["a"]}))


def test_wrong_input_type_raises_informative_error():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        clean_survey_scores([{"respondent_id": 1, "group": "a", "score": 1}])


def test_identical_valid_scores_get_zero_z_scores():
    df = pd.DataFrame(
        {"respondent_id": [1, 2], "group": ["A", "B"], "score": [5, 5]}
    )
    result = clean_survey_scores(df)
    np.testing.assert_allclose(result["score_z"].to_numpy(), [0.0, 0.0])


def test_all_scores_missing_or_negative_remain_missing():
    df = pd.DataFrame(
        {"respondent_id": [1, 2], "group": ["A", "B"], "score": [-999, -1]}
    )
    result = clean_survey_scores(df)
    assert result["score"].isna().all()
    assert result["score_z"].isna().all()


def test_one_valid_score_leaves_z_scores_missing():
    df = pd.DataFrame(
        {"respondent_id": [1, 2], "group": ["A", "B"], "score": [7, -999]}
    )
    result = clean_survey_scores(df)
    assert result["score_z"].isna().all()


def test_empty_dataframe_keeps_output_schema():
    df = pd.DataFrame(
        {
            "respondent_id": pd.Series(dtype="Int64"),
            "group": pd.Series(dtype="string"),
            "score": pd.Series(dtype="float64"),
        }
    )
    result = clean_survey_scores(df)
    assert result.empty
    assert list(result.columns) == [
        "respondent_id",
        "group",
        "score",
        "score_z",
    ]


def test_function_does_not_mutate_input():
    df = golden_input()
    original = df.copy(deep=True)
    clean_survey_scores(df)
    pd.testing.assert_frame_equal(df, original)


def test_invariants_for_nonconstant_valid_scores():
    df = golden_input()
    result = clean_survey_scores(df)
    valid = result["score_z"].dropna()
    assert len(result) <= len(df)
    assert valid.mean() == pytest.approx(0.0, abs=1e-12)
    assert valid.std(ddof=1) == pytest.approx(1.0, abs=1e-12)


def test_flag_outliers_identifies_values_beyond_threshold():
    df = pd.DataFrame(
        {
            "respondent_id": [1, 2, 3, 4, 5],
            "score_z": [-3.0, -2.5, 0.0, 2.5, 2.6],
        }
    )
    res = flag_outliers(df, threshold=2.5)
    assert res["is_outlier"].tolist() == [True, False, False, False, True]


def test_flag_outliers_missing_z_scores_are_false():
    df = pd.DataFrame(
        {
            "respondent_id": [1, 2],
            "score_z": [np.nan, 3.2],
        }
    )
    res = flag_outliers(df)
    assert res["is_outlier"].tolist() == [False, True]


def test_flag_outliers_missing_z_col_raises():
    df = pd.DataFrame({"respondent_id": [1], "val": [1.0]})
    with pytest.raises(ValueError, match="missing column: score_z"):
        flag_outliers(df)


def test_flag_outliers_wrong_type_raises():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        flag_outliers({"score_z": [1.0]})


def test_flag_outliers_does_not_mutate_input():
    df = pd.DataFrame({"respondent_id": [1, 2], "score_z": [3.0, 0.5]})
    original = df.copy(deep=True)
    flag_outliers(df)
    pd.testing.assert_frame_equal(df, original)
