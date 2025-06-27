import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load the training data
df = pd.read_csv('training_dataset.csv')

# Features and target
X = df[['is_home', 'opponent_id', 'goals_for', 'goals_against']]
y = df['result']

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained. Accuracy: {accuracy:.2f}")

# Save model
joblib.dump(model, 'match_predictor.pkl')
print("✅ Model saved to match_predictor.pkl")
