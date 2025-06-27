import json
import pandas as pd
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate training dataset from past.json'

    def handle(self, *args, **kwargs):
        try:
            with open('past.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write("❌ File 'past.json' not found.")
            return
        except json.JSONDecodeError:
            self.stderr.write("❌ Could not parse JSON.")
            return

        print("✅ Teams found in JSON:", list(data.keys()))

        training_data = []

        for team_name, matches in data.items():
            print(f"📊 Processing {team_name} - {len(matches)} matches")
            for match in matches:
                try:
                    home_name = match['home_team']['name'].lower()
                    away_name = match['away_team']['name'].lower()
                    team_key = team_name.lower()

                    is_home = home_name == team_key
                    opponent = match['away_team']['id'] if is_home else match['home_team']['id']
                    goals_for = match['home_goals'] if is_home else match['away_goals']
                    goals_against = match['away_goals'] if is_home else match['home_goals']

                    if goals_for is None or goals_against is None:
                        continue  # skip matches without complete score

                    if goals_for > goals_against:
                        result = 1
                    elif goals_for < goals_against:
                        result = -1
                    else:
                        result = 0

                    training_data.append({
                        'team': team_key,
                        'is_home': int(is_home),
                        'opponent_id': opponent,
                        'goals_for': goals_for,
                        'goals_against': goals_against,
                        'result': result
                    })
                except KeyError as e:
                    print(f"⚠️ Skipping invalid match entry: Missing key {e}")
                    continue

        df = pd.DataFrame(training_data)
        df.to_csv('training_dataset.csv', index=False)
        print(df.head())
        print(f"✅ training_dataset.csv created successfully with {len(df)} rows.")
