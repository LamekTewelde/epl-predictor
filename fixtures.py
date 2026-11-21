import requests

FIXTURES_URL = "https://fixturedownload.com/feed/json/epl-2026"

# fixturedownload.com and football-data.co.uk spell some teams differently.
# Map the fixtures site's names to the ones in our database; any name not listed
# is assumed to already match. If a fixture gets a null prediction for a team that
# should have history, its spelling is probably missing from here.
TEAM_NAME_FIXES = {
    "Man Utd": "Man United",
    "Manchester United": "Man United",
    "Manchester City": "Man City",
    "Spurs": "Tottenham",
    "Tottenham Hotspur": "Tottenham",
    "Nottingham Forest": "Nott'm Forest",
    "Wolverhampton": "Wolves",
    "Newcastle United": "Newcastle",
    "West Ham United": "West Ham",
    "Brighton & Hove Albion": "Brighton",
    "Leeds United": "Leeds",
}


def normalize_team(name):
    return TEAM_NAME_FIXES.get(name, name)


def get_next_round():
    response = requests.get(FIXTURES_URL, timeout=10)
    response.raise_for_status()  # fail loudly on a 404/500 instead of parsing an error page
    data = response.json()

    # Keep only matches that haven't been played yet
    unplayed = [match for match in data if match["HomeTeamScore"] is None]
    if not unplayed:
        return []  # season is over

    for match in unplayed:
        match["HomeTeam"] = normalize_team(match["HomeTeam"])
        match["AwayTeam"] = normalize_team(match["AwayTeam"])

    # Return only the earliest round among them
    next_round = min(match["RoundNumber"] for match in unplayed)
    return [match for match in unplayed if match["RoundNumber"] == next_round]
