import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv('training_dataset.csv')

# Feature columns
features = [
    'is_home',
    'opponent_id',
    'goals_for',
    'goals_against',
    'recent_win_rate',
    'recent_goal_diff',
    'form_score',
    'opponent_form_score'
]

X = df[features]
y = df['result'].replace({-1: 0, 0: 1, 1: 2})  # Encode target classes

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'scaler.pkl')  # Save for later prediction use

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Convert to PyTorch tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.long)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.long)

# Neural network definition
class MatchPredictor(nn.Module):
    def __init__(self, input_size):
        super(MatchPredictor, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # Output: 3 classes
        )

    def forward(self, x):
        return self.model(x)

# Instantiate model
model = MatchPredictor(input_size=X_train.shape[1])
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
epochs = 50
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

# Evaluation
model.eval()
with torch.no_grad():
    preds = model(X_test)
    y_pred = preds.argmax(dim=1)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {accuracy:.2f}")

# Save full model (arch + weights) to match_predictor.pkl
torch.save(model, 'match_predictor.pkl')
print("✅ Model saved as match_predictor.pkl")
