import joblib
import pandas as pd

model = joblib.load("model.joblib")

match = pd.DataFrame([{ "home_form": 3, "away_form": 13,
    "home_scored": 0.8, "away_scored": 2.4,
    "home_conceded": 2.2, "away_conceded": 0.6,}])

print(model.classes_)
print(model.predict_proba(match))