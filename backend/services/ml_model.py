import joblib
import os
import numpy as np

class PhishingModel:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        # Get path to: backend/services/ml_model.py
        current_file = os.path.abspath(__file__)
        
        # We need to go up 3 levels to reach the root 'WADE' folder
        # Level 1: backend/services
        # Level 2: backend
        # Level 3: WADE (Project Root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        
        # Now point to WADE/models/phishing_model.pkl
        model_path = os.path.join(project_root, "models", "phishing_model.pkl")

        try:
            self.model = joblib.load(model_path)
            print(f"🧠 AI Model loaded successfully from: {model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print(f"🔍 I looked in: {model_path}")
            self.model = None

    def predict(self, features):
        if not self.model:
            print("⚠️ Model not loaded, returning default score.")
            return 50.0  # Default to "Uncertain"

        # The model expects a list of lists (e.g., [[0, 1, 0...]])
        prediction = self.model.predict([features])[0]
        
        # We also want a probability score
        try:
            probability = self.model.predict_proba([features])[0][1]
            return probability * 100
        except:
            return float(prediction * 100)

# Create a global instance
ai_engine = PhishingModel()