from django.core.management.base import BaseCommand
from predictions.utils.save_matches import save_matches_from_json
import os

class Command(BaseCommand):
    help = 'Load matches from local JSON file'

    def handle(self, *args, **kwargs):
        self.stdout.write("📁 Loading from predictions/data/matches.json...")
        file_path = os.path.join("predictions", "data", "matches.json")
        save_matches_from_json(file_path)