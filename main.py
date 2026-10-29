from fastapi import FastAPI
from database import get_connection
from datetime import date
from pydantic import BaseModel
from features import get_form, get_goal_stats
import joblib
import pandas as pd

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/teams")
def teams():
    conn = get_connection()
    teams_rows = conn.execute("SELECT DISTINCT home_team FROM matches ORDER BY home_team").fetchall()
    teams_list = [team_row[0] for team_row in teams_rows]
    conn.close()
    return {"teams" : teams_list}

model = joblib.load("model.joblib")
FEATURES = ["home_form", "away_form", "home_scored", "away_scored", "home_conceded", "away_conceded"]

class MatchRequest(BaseModel):
    home_team: str
    away_team: str

@app.post("/predict")
def predict(match: MatchRequest):

    today = date.today().isoformat()
    conn = get_connection()

    home_team_form = get_form(conn, match.home_team, today)
    away_team_form = get_form(conn,match.away_team, today)

    home_team_score, home_team_conceed = get_goal_stats(conn, match.home_team, today)
    away_team_score, away_team_conceed = get_goal_stats(conn, match.away_team, today)

    conn.close()

    df = pd.DataFrame([{"home_form": home_team_form, "away_form": away_team_form,
    "home_scored": home_team_score, "away_scored": away_team_score,
    "home_conceded": home_team_conceed, "away_conceded": away_team_conceed,}])

    probs = model.predict_proba(df)[0]
    home = round(float(probs[2]),3)
    away = round(float(probs[0]),3)
    draw = round(float(probs[1]),3)

    return {"H":home,"D": draw, "A": away}
