from rest_framework.decorators import api_view
from rest_framework.response import Response
import joblib
import json

@api_view(['GET'])
def predict_winner(request):
    try:
        # Load upcoming match
        with open('matches.json', 'r') as f:
            matches = json.load(f)

        upcoming = next((m for m in matches if m.get("is_upcoming")), None)
        if not upcoming:
            return Response({"error": "No upcoming match found."})

        home_team = upcoming["home_team"]
        away_team = upcoming["away_team"]

        model = joblib.load("match_predictor.pkl")

        # Prepare features for both perspectives
        home_features = [[1, away_team["id"], 0, 0]]  # dummy goals for inference
        away_features = [[0, home_team["id"], 0, 0]]

        home_probs = model.predict_proba(home_features)[0]
        away_probs = model.predict_proba(away_features)[0]

        # Average both predictions
        avg_probs = (home_probs + away_probs) / 2

        result_map = {-1: "Loss", 0: "Draw", 1: "Win"}
        classes = model.classes_

        best_index = avg_probs.argmax()
        best_class = classes[best_index]
        confidence = round(avg_probs[best_index] * 100, 2)

        if best_class == 1:
            result = f"{home_team['name']} will win"
        elif best_class == -1:
            result = f"{away_team['name']} will win"
        else:
            result = "It will be a draw"

        return Response({
            "home_team": home_team["name"],
            "away_team": away_team["name"],
            "prediction": result,
            "confidence": f"{confidence}%"
        })

    except FileNotFoundError:
        return Response({"error": "matches.json not found"})
    except Exception as e:
        return Response({"error": str(e)})
