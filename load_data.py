import pandas as pd
import sqlite3
from database import get_connection 

df = pd.read_csv('data/E0.csv', usecols =['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR'])
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
df["season"] = "2025-26"
rows = list(df[["season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]].itertuples(index=False, name=None))

conn = get_connection()

conn.executemany("INSERT INTO matches (season, match_date, home_team, away_team, home_goals, away_goals, result) VALUES (?,?,?,?,?,?,?) ON CONFLICT DO NOTHING", rows)

conn.commit()
count = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
print(count)
conn.close()


