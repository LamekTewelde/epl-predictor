from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from database import get_connection
from features import build_dataset
import pandas as pd

def main():
    conn = get_connection()
    df = build_dataset(conn)
    conn.close()

    mask = df["match_date"] >= "2025-08-01"

    train_set = df[~mask].copy()
    test_set = df[mask].copy()

    X_train = train_set[["home_form","away_form",'home_scored', 'away_scored', 'home_conceded', 'away_conceded']]
    Y_train = train_set["result"]

    X_test = test_set[["home_form","away_form",'home_scored', 'away_scored', 'home_conceded', 'away_conceded']]
    Y_test = test_set["result"]

    model = LogisticRegression()
    #Where learning happens
    model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)

    accuracy = accuracy_score(Y_test, Y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    baseline = (Y_test == "H").mean()
    print(f"Baseline (always H): {baseline * 100:.2f}%")
    print(pd.Series(Y_pred).value_counts())
if __name__ == "__main__":
    main()





