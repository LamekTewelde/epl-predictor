from database import get_connection
import pandas as pd

# The model's inputs, in the order it was trained on. Every file imports this list
# so the column order can't drift between training and prediction.
FEATURES = ["home_form", "away_form", "home_scored", "away_scored", "home_conceded", "away_conceded"]


def get_last_matches(conn, team, date):
    """The team's 5 most recent matches strictly before `date` (no data leakage)."""
    query = """
    SELECT match_date, home_team, away_team, home_goals, away_goals, result
    FROM matches
    WHERE (home_team = ? OR away_team = ?) AND match_date < ?
    ORDER BY match_date DESC
    LIMIT 5;
    """
    return conn.execute(query, (team, team, date)).fetchall()


def get_form(conn, team, date):
    """Points from the last 5 matches (win = 3, draw = 1), or None if fewer than 5."""
    matches = get_last_matches(conn, team, date)
    if len(matches) < 5:
        return None

    points = 0
    for match_date, home_team, away_team, home_goals, away_goals, result in matches:
        if result == "D":
            points += 1
        elif (home_team == team and result == "H") or (away_team == team and result == "A"):
            points += 3
    return points


def get_goal_stats(conn, team, date):
    """Average goals scored and conceded over the last 5 matches, or None if fewer than 5."""
    matches = get_last_matches(conn, team, date)
    if len(matches) < 5:
        return None

    scored = 0
    conceded = 0
    for match_date, home_team, away_team, home_goals, away_goals, result in matches:
        if home_team == team:
            scored += home_goals
            conceded += away_goals
        else:
            scored += away_goals
            conceded += home_goals
    return scored / 5, conceded / 5


def team_exists(conn, team):
    row = conn.execute(
        "SELECT 1 FROM matches WHERE home_team = ? OR away_team = ? LIMIT 1",
        (team, team),
    ).fetchone()
    return row is not None


def build_dataset(conn):
    """One row per match: both teams' features going into it, plus the real result."""
    all_matches = conn.execute(
        "SELECT match_date, home_team, away_team, result FROM matches ORDER BY match_date"
    ).fetchall()

    data = []
    for match_date, home_team, away_team, result in all_matches:
        home_form = get_form(conn, home_team, match_date)
        away_form = get_form(conn, away_team, match_date)
        # get_goal_stats returns None in exactly the same case as get_form (< 5 matches),
        # so checking the form values is enough to make the unpacking below safe
        if home_form is None or away_form is None:
            continue

        home_scored, home_conceded = get_goal_stats(conn, home_team, match_date)
        away_scored, away_conceded = get_goal_stats(conn, away_team, match_date)

        data.append((match_date, home_team, away_team, home_form, away_form,
                     home_scored, away_scored, home_conceded, away_conceded, result))

    return pd.DataFrame(data, columns=["match_date", "home_team", "away_team", *FEATURES, "result"])


if __name__ == "__main__":
    conn = get_connection()
    df = build_dataset(conn)
    print(len(df))
    print(df.head())
    print(df["result"].value_counts())
    conn.close()
