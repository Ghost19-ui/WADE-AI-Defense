import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import requests
from feature_extractor import FeatureExtractor

# --- CONFIGURATION ---
DATASET_URL = "https://raw.githubusercontent.com/Komal01/phishing-URL-detection/master/dataset2.csv"

def download_dataset(filepath):
    print(f"📥 Downloading dataset...")
    try:
        response = requests.get(DATASET_URL)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print("✅ Dataset downloaded!")
        else:
            print(f"❌ Download failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def load_real_data(csv_path):
    # 1. Download if missing
    if not os.path.exists(csv_path):
        download_dataset(csv_path)

    print(f"📂 Loading data from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        
        # --- THE FIX: CLEAN BAD DATA ---
        # This removes the empty rows that caused your crash
        df = df.dropna(subset=['URL']) 
        df['URL'] = df['URL'].astype(str)
        
        # Take a sample (Max 2000 rows)
        sample_size = min(2000, len(df))
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
        
        print(f"📊 Processing {len(df)} URLs...")
        
        features_list = []
        labels = []
        
        for index, row in df.iterrows():
            url = row['URL']
            target = row['Target'] 
            
            # Label: 1=Phishing, 0=Safe
            label = 1 if str(target).lower() in ['yes', 'phishing', 'bad'] else 0
            
            # Use Dummy HTML to speed up training
            dummy_html = "<html><body></body></html>"
            
            try:
                extractor = FeatureExtractor(url, html_content=dummy_html)
                features = extractor.extract()
                features_list.append(features)
                labels.append(label)
            except:
                continue # Skip bad URLs silently
            
            if index % 200 == 0:
                print(f"   Processed {index}...")

        return np.array(features_list), np.array(labels)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def train():
    # Find project paths
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    dataset_path = os.path.join(project_root, "backend", "datasets", "dataset.csv")
    models_dir = os.path.join(project_root, "models")
    
    # Load and Train
    if not os.path.exists(os.path.dirname(dataset_path)):
        os.makedirs(os.path.dirname(dataset_path))

    X, y = load_real_data(dataset_path)
    
    if X is None or len(X) == 0:
        print("❌ No data found.")
        return

    print("🧠 Training AI Model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"✅ Model Trained! Accuracy: {acc * 100:.2f}%")
    
    # Save Model
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        
    joblib.dump(model, os.path.join(models_dir, "phishing_model.pkl"))
    print(f"💾 Saved to {models_dir}")

if __name__ == "__main__":
    train()