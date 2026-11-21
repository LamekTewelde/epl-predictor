"""Train the model on every match in the database and save it to model.joblib.

To see how well the model does on matches it hasn't seen, run evaluate.py.
"""
import joblib
from sklearn.linear_model import LogisticRegression

from database import get_connection
from features import FEATURES, build_dataset


def main():
    conn = get_connection()
    df = build_dataset(conn)
    conn.close()

    model = LogisticRegression()
    model.fit(df[FEATURES], df["result"])  # where the learning happens
    joblib.dump(model, "model.joblib")
    print(f"Model trained on {len(df)} matches and saved")


if __name__ == "__main__":
    main()
