from rest_framework.decorators import api_view
from rest_framework.response import Response
import joblib
import json

@api_view(['GET'])
def predict_winner(request):
    try:
        # Load the matches JSON (must be a list of team blocks)
        with open('matches.json', 'r') as f:
            data = json.load(f)

        # Flatten all matches from both teams
        if isinstance(data, dict) and "matches" in data:
            team_blocks = data["matches"]
        elif isinstance(data, list):
            team_blocks = data
        else:
            return Response({"error": "Invalid format: top-level JSON must be a list or have 'matches' key."})

        all_matches = []
        for team_block in team_blocks:
            all_matches.extend(team_block.get("matches", []))

        # Find upcoming match
        upcoming = next((m for m in all_matches if m.get("is_upcoming")), None)
        if not upcoming:
            return Response({"error": "No upcoming match found."})

        # Get home and away team using either structure
        if "teams" in upcoming:
            home_team = upcoming["teams"].get("home")
            away_team = upcoming["teams"].get("away")
        elif "home_team" in upcoming and "away_team" in upcoming:
            home_team = upcoming["home_team"]
            away_team = upcoming["away_team"]
        else:
            return Response({"error": "Invalid match format: missing 'teams' or 'home_team/away_team'"})

        if not home_team or not away_team:
            return Response({"error": "Home or away team data is missing."})

        # Load the trained model
        model = joblib.load("match_predictor.pkl")

        # Prepare features (goals = 0 as dummy input)
        home_features = [[1, away_team["id"], 0, 0]]
        away_features = [[0, home_team["id"], 0, 0]]

        home_probs = model.predict_proba(home_features)[0]
        away_probs = model.predict_proba(away_features)[0]

        avg_probs = (home_probs + away_probs) / 2

        classes = model.classes_
        best_index = avg_probs.argmax()
        best_class = classes[best_index]
        confidence = round(avg_probs[best_index] * 100, 2)

        if best_class == 1:
            prediction = f"{home_team['name']} will win"
        elif best_class == -1:
            prediction = f"{away_team['name']} will win"
        else:
            prediction = "It will be a draw"

        return Response({
            "home_team": home_team["name"],
            "away_team": away_team["name"],
            "prediction": prediction,
            "confidence": f"{confidence}%"
        })

    except FileNotFoundError:
        return Response({"error": "matches.json not found"})
    except Exception as e:
        return Response({"error": str(e)})
