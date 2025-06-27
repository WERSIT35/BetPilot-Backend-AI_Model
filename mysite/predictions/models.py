from django.db import models

class Team(models.Model):
    team_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Match(models.Model):
    id = models.AutoField(primary_key=True)
    fixture_id = models.IntegerField(unique=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=10)
    league_name = models.CharField(max_length=100)
    season = models.IntegerField()
    home_goals = models.IntegerField(null=True, blank=True)
    away_goals = models.IntegerField(null=True, blank=True)
    winner = models.CharField(max_length=100, null=True, blank=True)
    is_upcoming = models.BooleanField()

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
