from database import get_connection
import pandas as pd

def get_last_matches(conn, team, date):
    query = """
    SELECT match_date, home_team, away_team, home_goals, away_goals, result
    FROM matches
    WHERE (home_team = ? OR away_team = ?) AND ? > match_date
    ORDER BY match_date DESC
    LIMIT 5;
    """
    return conn.execute(query,(team, team, date)).fetchall()

def get_form(conn,team,date):
    matches = get_last_matches(conn, team, date)

    if len(matches) < 5:
        return None
    
    points = 0

    for match_date, home_team, away_team, home_goals, away_goals, result in matches:
        if (home_team == team) and result == 'H':
            points += 3
        elif (home_team == team) and result == 'A':
            points += 0
        elif (home_team == team or away_team == team) and result == 'D':
            points += 1
        elif (away_team == team) and result == 'A':
            points += 3
        elif (away_team == team) and result == 'H':
            points += 0

    return points 
def get_goal_stats(conn, team, date):

    matches = get_last_matches(conn, team, date)
    if len(matches) < 5:
        return None
    

    score = 0
    conceed = 0

    for match_date, home_team, away_team, home_goals, away_goals, result in matches:
        if home_team == team:
            score += home_goals
            conceed += away_goals
        elif away_team == team:
            score += away_goals
            conceed += home_goals
    
    return score / 5, conceed / 5


def team_exists(conn,team):
    row = conn.execute("SELECT home_team, away_team FROM matches WHERE (home_team = ?) OR (away_team = ?) LIMIT 1", (team,team)).fetchone()

    return row is not None


def build_dataset(conn):
    all_matches = conn.execute("SELECT match_date, home_team, away_team, result FROM matches ORDER BY match_date").fetchall()
    
    data = []
    for match_date, home_team, away_team, result in all_matches:
        home_team_form = get_form(conn,home_team,match_date)
        away_team_form = get_form(conn, away_team, match_date)

        home_stats = get_goal_stats(conn,home_team, match_date)
        away_stats = get_goal_stats(conn,away_team, match_date)
        

        if home_team_form is None or away_team_form is None:
            continue
        if home_stats is None or away_stats is None:
            continue

        home_scored , home_conceded = home_stats
        away_scored , away_conceded = away_stats
        
        data.append((match_date, home_team,away_team,home_team_form,away_team_form, home_scored, away_scored, home_conceded, away_conceded, result))
        
    training_set = pd.DataFrame(data, columns = ['match_date','home_team','away_team','home_form', 'away_form', 'home_scored',  'away_scored', 'home_conceded', 'away_conceded', 'result'])

    return training_set



if __name__ == "__main__":
    conn = get_connection()
    df = build_dataset(conn)
    print(len(df))
    print(df.head())
    print(df["result"].value_counts())
    conn.close()