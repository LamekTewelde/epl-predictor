from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from database import get_connection
from features import build_dataset
import pandas as pd
import joblib


def main():
    conn = get_connection()
    df = build_dataset(conn)
    conn.close()

    FEATURES = ["home_form","away_form",'home_scored', 'away_scored', 'home_conceded', 'away_conceded']

    model = LogisticRegression()
    #Where learning happens
    model.fit(df[FEATURES], df["result"])
    joblib.dump(model, "model.joblib" )
    print("model saved")
if __name__ == "__main__":
    main()





