CREATE TABLE IF NOT EXISTS matches(
    id INTEGER PRIMARY KEY,
    season TEXT NOT NULL,
    match_date TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('H', 'D', 'A')),
    UNIQUE(home_team, away_team, season)
);