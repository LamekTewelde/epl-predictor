"""Measure the model honestly: train on older seasons, test on a season it has never seen.

Reproduces the result in the README:
    train = 2022-23 to 2024-25, test = 2025-26
The split is by date, not random, so the model never learns from the future.
"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from database import get_connection
from features import FEATURES, build_dataset

TEST_START = "2025-08-01"  # first day of the 2025-26 season
TEST_END = "2026-08-01"    # first day of 2026-27, kept out of this test


def main():
    conn = get_connection()
    df = build_dataset(conn)
    conn.close()

    train = df[df["match_date"] < TEST_START]
    test = df[(df["match_date"] >= TEST_START) & (df["match_date"] < TEST_END)]

    model = LogisticRegression()
    model.fit(train[FEATURES], train["result"])
    predictions = model.predict(test[FEATURES])

    accuracy = accuracy_score(test["result"], predictions)
    baseline = (test["result"] == "H").mean()  # always guessing a home win

    print(f"Trained on {len(train)} matches, tested on {len(test)}")
    print(f"Model accuracy:       {accuracy * 100:.1f}%")
    print(f"Baseline (always H):  {baseline * 100:.1f}%")
    print("Predictions made:")
    print(pd.Series(predictions).value_counts().to_string())


if __name__ == "__main__":
    main()
