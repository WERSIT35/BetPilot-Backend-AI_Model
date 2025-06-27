import json
from predictions.models import Match, Team

def save_matches_from_json(file_path):
    with open(file_path, 'r') as f:
        matches = json.load(f)

    for match_data in matches:
        home_team_data = match_data['home_team']
        away_team_data = match_data['away_team']

        home_team, _ = Team.objects.get_or_create(
            team_id=home_team_data['id'],
            defaults={'name': home_team_data['name']}
        )

        away_team, _ = Team.objects.get_or_create(
            team_id=away_team_data['id'],
            defaults={'name': away_team_data['name']}
        )

        Match.objects.update_or_create(
            fixture_id=match_data['fixture_id'],
            defaults={
                'date': match_data['date'],
                'status': match_data['status'],
                'league_name': match_data['league_name'],
                'season': match_data['season'],
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': match_data['home_goals'],
                'away_goals': match_data['away_goals'],
                'winner': match_data['winner'],
                'is_upcoming': match_data['is_upcoming'],
            }
        )
