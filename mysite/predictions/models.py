from django.db import models

class Team(models.Model):
    team_id = models.IntegerField(unique=True)  # external API ID
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Match(models.Model):
    fixture_id = models.IntegerField(unique=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=20)
    league_name = models.CharField(max_length=100)
    season = models.IntegerField()
    
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')

    home_goals = models.IntegerField(null=True, blank=True)
    away_goals = models.IntegerField(null=True, blank=True)

    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_matches')
    
    is_upcoming = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.date.strftime('%Y-%m-%d')})"

    def result_for(self, team: Team):
        if self.winner is None:
            return 0  # draw
        elif self.winner == team:
            return 1  # win
        else:
            return -1  # loss

    def goal_difference_for(self, team: Team):
        if team == self.home_team:
            return (self.home_goals or 0) - (self.away_goals or 0)
        elif team == self.away_team:
            return (self.away_goals or 0) - (self.home_goals or 0)
        return 0
