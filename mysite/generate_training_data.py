import json
import pandas as pd
from datetime import datetime

# ---- Configuration ----
MATCH_FILE = 'matches.json'
OUTPUT_FILE = 'training_dataset.csv'
FORM_WINDOW = 5  # number of recent matches to consider for form stats

# ---- Load matches ----
with open(MATCH_FILE, 'r') as f:
    data = json.load(f)

# Flatten matches by team
team_matches = {}
for team_entry in data:
    team = team_entry['team']
    matches = team_entry['matches']
    team_matches[team] = sorted(matches, key=lambda x: x['date'])  # sort chronologically

# ---- Helper Functions ----
def get_result(match, team_id):
    winner = match.get("winner")
    if winner is None:
        return 0
    if winner == match['teams']['home']['name'] and match['teams']['home']['id'] == team_id:
        return 1
    if winner == match['teams']['away']['name'] and match['teams']['away']['id'] == team_id:
        return 1
    return -1

def get_goals(match, team_id):
    home = match['teams']['home']['id']
    if home == team_id:
        return match['goals']['home'], match['goals']['away']
    else:
        return match['goals']['away'], match['goals']['home']

def get_form_stats(matches, team_id, current_date):
    recent = [
        m for m in matches 
        if not m['is_upcoming'] and m['date'] < current_date
        and (m['teams']['home']['id'] == team_id or m['teams']['away']['id'] == team_id)
    ]
    recent = sorted(recent, key=lambda x: x['date'], reverse=True)[:FORM_WINDOW]
    
    if not recent:
        return 0, 0, 0  # fallback

    wins = sum(1 for m in recent if get_result(m, team_id) == 1)
    goal_diff = sum(get_goals(m, team_id)[0] - get_goals(m, team_id)[1] for m in recent)
    score = sum(3 if get_result(m, team_id) == 1 else 1 if get_result(m, team_id) == 0 else 0 for m in recent)

    return wins / FORM_WINDOW, goal_diff / FORM_WINDOW, score

# ---- Build dataset ----
rows = []
for team_name, matches in team_matches.items():
    for match in matches:
        if match['is_upcoming']:
            continue  # skip future matches

        date = match['date']
        try:
            match_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except Exception:
            continue

        home_id = match['teams']['home']['id']
        away_id = match['teams']['away']['id']

        for is_home, team_id, opp_id in [(True, home_id, away_id), (False, away_id, home_id)]:
            goals_for, goals_against = get_goals(match, team_id)
            result = get_result(match, team_id)

            win_rate, goal_diff, form_score = get_form_stats(matches, team_id, match['date'])
            opp_win_rate, _, opp_form_score = get_form_stats(matches, opp_id, match['date'])

            row = {
                "is_home": int(is_home),
                "opponent_id": opp_id,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "recent_win_rate": round(win_rate, 2),
                "recent_goal_diff": round(goal_diff, 2),
                "form_score": form_score,
                "opponent_form_score": opp_form_score,
                "result": result
            }
            rows.append(row)

# ---- Save CSV ----
df = pd.DataFrame(rows)
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved {len(df)} rows to {OUTPUT_FILE}")
