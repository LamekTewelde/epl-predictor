import requests

FIXTURES_URL = "https://fixturedownload.com/feed/json/epl-2026"


def get_next_round():
    response = requests.get(FIXTURES_URL, timeout=10)
    response.raise_for_status()  # crash loudly on a 404/500 instead of parsing an error page
    data = response.json()

    # Pass 1: keep only matches that haven't been played yet
    unplayed = [match for match in data if match["HomeTeamScore"] is None]
    if not unplayed:
        return []  # season is over

    # Pass 2: find the earliest round among them
    smallest_round = min(match["RoundNumber"] for match in unplayed)
    
    for match in unplayed:
        match["HomeTeam"] = match["HomeTeam"].replace("Man Utd", "Man United")
        match["AwayTeam"] = match["AwayTeam"].replace("Man Utd", "Man United")
        match["HomeTeam"] = match["HomeTeam"].replace("Spurs", "Tottenham")
        match["AwayTeam"] = match["AwayTeam"].replace("Spurs", "Tottenham")


    # Pass 3: return only the matches in that round
    return [match for match in unplayed if match["RoundNumber"] == smallest_round]
