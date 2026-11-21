from datetime import date

import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from database import get_connection
from features import FEATURES, get_form, get_goal_stats, team_exists
from fixtures import get_next_round

app = FastAPI()
model = joblib.load("model.joblib")  # loaded once at startup, not on every request


class MatchRequest(BaseModel):
    home_team: str
    away_team: str


def predict_match(conn, home_team, away_team, on_date):
    """Return {"H", "D", "A"} probabilities, or None if either team lacks 5 earlier matches.
    Does not close conn: the caller opened it, so the caller closes it."""
    home_form = get_form(conn, home_team, on_date)
    away_form = get_form(conn, away_team, on_date)
    # get_goal_stats returns None in exactly the same case as get_form,
    # so this check also makes the unpacking below safe
    if home_form is None or away_form is None:
        return None

    home_scored, home_conceded = get_goal_stats(conn, home_team, on_date)
    away_scored, away_conceded = get_goal_stats(conn, away_team, on_date)

    row = pd.DataFrame([{
        "home_form": home_form, "away_form": away_form,
        "home_scored": home_scored, "away_scored": away_scored,
        "home_conceded": home_conceded, "away_conceded": away_conceded,
    }])[FEATURES]

    probs = dict(zip(model.classes_, model.predict_proba(row)[0]))
    return {result: round(float(probs[result]), 3) for result in ("H", "D", "A")}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams")
def teams():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT home_team FROM matches ORDER BY home_team").fetchall()
    finally:
        conn.close()
    return {"teams": [row[0] for row in rows]}


@app.post("/predict")
def predict(match: MatchRequest):
    if match.home_team == match.away_team:
        raise HTTPException(status_code=400, detail="Home and away teams must be different")

    conn = get_connection()
    try:  # finally closes the connection even when an HTTPException is raised
        for team in (match.home_team, match.away_team):
            if not team_exists(conn, team):
                raise HTTPException(status_code=404, detail=f"Team not found: {team}")
        result = predict_match(conn, match.home_team, match.away_team, date.today().isoformat())
    finally:
        conn.close()

    if result is None:
        raise HTTPException(status_code=400, detail="Not enough recent matches for one of the teams")
    return result


@app.get("/fixtures/upcoming")
def upcoming_fixtures():
    try:
        matches = get_next_round()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Fixture source unavailable, try again later")

    conn = get_connection()
    try:
        fixtures = [
            {
                "home_team": match["HomeTeam"],
                "away_team": match["AwayTeam"],
                "kickoff": match["DateUtc"],
                # "2026-11-21 12:30:00Z" -> "2026-11-21": only matches before kickoff count
                "prediction": predict_match(conn, match["HomeTeam"], match["AwayTeam"], match["DateUtc"][:10]),
            }
            for match in matches
        ]
    finally:
        conn.close()

    round_number = matches[0]["RoundNumber"] if matches else None
    return {"round": round_number, "fixtures": fixtures}
