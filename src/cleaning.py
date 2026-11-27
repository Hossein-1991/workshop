"""Pure survey cleaning and score standardization."""
import numpy as np
import pandas as pd

_REQUIRED_COLUMNS = ("respondent_id", "group", "score")


def clean_survey_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of survey responses.

    Rows without respondent IDs are dropped. Group labels are stripped and
    lowercased. Negative scores are treated as missing. score_z uses the
    sample standard deviation (ddof=1) over valid scores. If at least two
    valid scores exist and their standard deviation is zero, valid scores get
    a z-score of 0.0. With fewer than two valid scores, score_z is missing
    for every row because the sample standard deviation is undefined.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing = sorted(set(_REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(
            "df is missing required columns: " + ", ".join(missing)
        )

    cleaned = df.loc[df["respondent_id"].notna(), list(_REQUIRED_COLUMNS)].copy()
    cleaned["group"] = cleaned["group"].astype("string").str.strip().str.lower()
    cleaned["score"] = pd.to_numeric(cleaned["score"], errors="raise")
    cleaned.loc[cleaned["score"] < 0, "score"] = np.nan

    valid_scores = cleaned["score"].dropna()
    if len(valid_scores) < 2:
        cleaned["score_z"] = np.nan
    else:
        sample_sd = float(valid_scores.std(ddof=1))
        if sample_sd == 0.0:
            cleaned["score_z"] = cleaned["score"].where(
                cleaned["score"].isna(), 0.0
            )
        else:
            cleaned["score_z"] = (
                cleaned["score"] - float(valid_scores.mean())
            ) / sample_sd

    return cleaned
