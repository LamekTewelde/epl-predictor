from fastapi import FastAPI
from fastapi import HTTPException
from database import get_connection
from datetime import date
from pydantic import BaseModel
from features import get_form, get_goal_stats,team_exists
import joblib
import pandas as pd
from fastapi.responses import RedirectResponse
from fixtures import get_next_round
import requests

app = FastAPI()
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

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

def predict_match(conn, home_team, away_team, on_date):
    """Return {"H", "D", "A"} probabilities, or None if either team lacks 5 earlier matches.
    Does not close conn: the caller opened it, so the caller closes it."""
    home_team_form = get_form(conn, home_team, on_date)
    away_team_form = get_form(conn, away_team, on_date)

    if home_team_form is None or away_team_form is None:
        return None

    home_team_score, home_team_conceed = get_goal_stats(conn, home_team, on_date)
    away_team_score, away_team_conceed = get_goal_stats(conn, away_team, on_date)

    df = pd.DataFrame([{"home_form": home_team_form, "away_form": away_team_form,
    "home_scored": home_team_score, "away_scored": away_team_score,
    "home_conceded": home_team_conceed, "away_conceded": away_team_conceed,}])

    probs = model.predict_proba(df)[0]
    home = round(float(probs[2]),3)
    away = round(float(probs[0]),3)
    draw = round(float(probs[1]),3)

    return {"H":home,"D": draw, "A": away}


class MatchRequest(BaseModel):
    home_team: str
    away_team: str

@app.post("/predict")
def predict(match: MatchRequest):
    
    if match.home_team == match.away_team:
        raise HTTPException(status_code=400, detail="Home and Away team must be different")
    
    today = date.today().isoformat()
    conn = get_connection()

    if (team_exists(conn,match.home_team) == False):
        conn.close()
        raise HTTPException(status_code= 404, detail=f"Team not found: {match.home_team}")
    if (team_exists(conn,match.away_team) == False):
        conn.close()
        raise HTTPException(status_code= 404, detail=f"Team not found: {match.away_team}")
    
    results = predict_match(conn, match.home_team, match.away_team, today)
    conn.close()  # close before checking, so the None path doesn't leak the connection

    if results is None:
        raise HTTPException(status_code=400, detail="Not enough recent matches for one of the teams")

    return results


@app.get("/fixtures/upcoming")
def upcoming_fixtures():
    try:
        matches = get_next_round()
    except requests.RequestException:
        # The fixtures site is down or slow: that's not our bug, so say so with a 503
        raise HTTPException(status_code=503, detail="Fixture source unavailable, try again later")

    conn = get_connection()
    fixtures = []
    for match in matches:
        kickoff_date = match["DateUtc"][:10]  # "2026-11-21 12:30:00Z" -> "2026-11-21"
        fixtures.append({
            "home_team": match["HomeTeam"],
            "away_team": match["AwayTeam"],
            "kickoff": match["DateUtc"],
            "prediction": predict_match(conn, match["HomeTeam"], match["AwayTeam"], kickoff_date),
        })
    conn.close()

    round_number = matches[0]["RoundNumber"] if matches else None
    return {"round": round_number, "fixtures": fixtures}
