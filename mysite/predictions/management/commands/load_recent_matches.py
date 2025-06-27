import os
import json
from django.core.management.base import BaseCommand
from predictions.models import Match, Team

class Command(BaseCommand):
    help = "Load recent matches from a JSON file into the database"

    def handle(self, *args, **kwargs):
        file_path = os.path.join("predictions", "data", "recent_matches.json")
        self.stdout.write(f"📁 Loading {file_path}...")

        with open(file_path, "r") as f:
            data = json.load(f)

        count = 0
        for match in data:
            home_team, _ = Team.objects.get_or_create(
                team_id=match["home_team"]["id"], defaults={"name": match["home_team"]["name"]}
            )
            away_team, _ = Team.objects.get_or_create(
                team_id=match["away_team"]["id"], defaults={"name": match["away_team"]["name"]}
            )

            Match.objects.update_or_create(
                fixture_id=match["fixture_id"],
                defaults={
                    "home_team": home_team,
                    "away_team": away_team,
                    "date": match["date"],
                    "status": match["status"],
                    "league_name": match["league_name"],
                    "season": match["season"],
                    "home_goals": match["home_goals"],
                    "away_goals": match["away_goals"],
                    "winner": match["winner"],
                    "is_upcoming": match["is_upcoming"],
                },
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Loaded {count} recent matches."))
