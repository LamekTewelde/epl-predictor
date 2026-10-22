from database import get_connection

def get_last_matches(conn, team, date):
    query = """
    SELECT match_date, home_team, away_team, result
    FROM matches
    WHERE (home_team = ? OR away_team = ?) AND ? > match_date
    ORDER BY match_date DESC
    LIMIT 5;
    """
    return conn.execute(query,(team, team, date)).fetchall()

def get_form(conn,team,date):
    matches = get_last_matches(conn, team, date)
    points = 0

    for match_date, home_team, away_team, result in matches:
        if (home_team == team or away_team == team) and result == 'H':
            points += 3
        elif (home_team == team or away_team == team) and result == 'D':
            points += 1
        elif (home_team == team or away_team == team) and result == 'L':
            points += 0

    return points 




if __name__ == "__main__":
    conn = get_connection()
    for row in get_last_matches(conn, "Arsenal", "2026-05-01"):
        print(row)
    print("Form:", get_form(conn, "Arsenal", "2026-05-01"))
    conn.close()