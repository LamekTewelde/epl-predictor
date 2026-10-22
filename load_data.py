import pandas as pd
from database import get_connection 



def load_season(conn, code):

    url = f"https://www.football-data.co.uk/mmz4281/{code}/E0.csv"
    df = pd.read_csv(url, usecols =['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    season = f"20{code[:2]}-{code[2:]}"
    df["season"] = season
    rows = list(df[["season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]].itertuples(index=False, name=None))

    
    conn.executemany("INSERT INTO matches (season, match_date, home_team, away_team, home_goals, away_goals, result) VALUES (?,?,?,?,?,?,?) ON CONFLICT DO NOTHING", rows)
    conn.commit()



def main():
    conn = get_connection()

    for code in ["2223", "2324", "2425","2526"]:
        load_season(conn, code)
        print("Loaded", code)

    count = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    print(count)
    conn.close()

if __name__ == "__main__":
    main()