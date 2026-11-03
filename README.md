# Premier League Match Predictor API

A REST API that predicts the outcome of Premier League matches. Give it two teams and it returns the probability of a home win, a draw or an away win, based on each team's recent form.

**Live demo:** https://epl-predictor-vbj3.onrender.com
*(Hosted on Render's free tier: the first request may take about a minute while the server wakes up.)*

## How it works

1. **Data:** match results for every Premier League season from 2022-23 to the current season are downloaded from [football-data.co.uk](https://www.football-data.co.uk/) and stored in SQLite. Re-running the loader skips matches already saved, so it is safe to run again.
2. **Features:** for each match, the API looks at each team's **last 5 matches before that date**: points earned (form), and average goals scored and conceded. Only earlier matches are used, so the model never sees the result it is predicting (no data leakage).
3. **Model:** a scikit-learn logistic regression trained on those six features, returning probabilities for home win, draw and away win.
4. **API:** FastAPI serves the predictions, computing each team's current form from the database at request time.

## Results

The model was trained on 2022-23 to 2024-25 and tested on the full 2025-26 season, which it had never seen.

| Approach | Accuracy |
|---|---|
| Baseline: always predict a home win | 42.4% |
| **This model** | **46.4%** |

The baseline matters because home teams win more often than any other result, so a model that only guesses "home win" already scores 42%. This model beats it by about 4 points, roughly 15 more correct predictions across the season.

## Example

**Request**

```http
POST /predict
Content-Type: application/json

{"home_team": "Arsenal", "away_team": "Chelsea"}
```

**Response**

```json
{"H": 0.538, "D": 0.251, "A": 0.211}
```

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks the server is running |
| GET | `/teams` | Lists every team in the database |
| POST | `/predict` | Returns home win / draw / away win probabilities for two teams |

Bad requests return clear errors: **404** for an unknown team, **400** if both teams are the same or a team doesn't have enough recent matches.

Interactive documentation is available at [`/docs`](https://epl-predictor-vbj3.onrender.com/docs).

## Tech stack

Python · FastAPI · SQLite · pandas · scikit-learn · pytest · Docker · Render

## Project structure

| File | Purpose |
|---|---|
| `schema.sql` | Database table definition |
| `database.py` | Opens the database connection and creates the table |
| `load_data.py` | Downloads each season and loads it into SQLite |
| `features.py` | Calculates form and goal stats, and builds the training dataset |
| `model.py` | Trains and evaluates the model, then saves it to `model.joblib` |
| `main.py` | The FastAPI app |
| `test_api.py` | Automated API tests |

## Run locally

Requires Python 3.10.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python3 load_data.py             # download match data into SQLite
python3 model.py                 # train, evaluate and save the model
uvicorn main:app --reload        # start the API
```

Then open http://127.0.0.1:8000/docs.

**With Docker**

```bash
docker build -t epl-predictor .
docker run -p 8000:8000 epl-predictor
```

**Tests**

```bash
pytest
```

## What I'd improve next

- **Better features:** home and away form tracked separately, head-to-head record, and longer-term team strength ratings.
- **Draw prediction:** the model rarely predicts draws, a common weakness in football models. Adjusting class weights could help.
- **Automatic data refresh:** a scheduled job to load new results each week, so predictions stay current without a redeploy.
- **Front end:** a React app where users pick two teams and see the probabilities visually.
