import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os

INPUT_FILE = "short_trade_labels.csv"
MODEL_FILE = "short_trade_model.pkl"
ENCODER_FILE = "short_ticker_encoder.pkl"

# Check if the labeled file exists
if not os.path.exists(INPUT_FILE):
    print(f"❌ {INPUT_FILE} not found. Run label_short_trades.py first.")
    exit()

# === Load Labeled Data ===
df = pd.read_csv(INPUT_FILE)

if df.empty:
    print("⚠️ No labeled data to train on yet.")
    exit()

# === Encode Labels
label_map = {"WIN": 2, "NEUTRAL": 1, "LOSS": 0}
df["label_encoded"] = df["label"].map(label_map)

# === Encode Ticker Symbol
ticker_encoder = LabelEncoder()
df["ticker_encoded"] = ticker_encoder.fit_transform(df["ticker"])

# === Features and Labels
features = df[["ticker_encoded", "entry_price", "exit_price", "pct_change"]]
labels = df["label_encoded"]

# === Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# === Train Model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# === Evaluate
y_pred = clf.predict(X_test)
print("\n📊 Model Evaluation:")
from sklearn.utils.multiclass import unique_labels
labels_present = unique_labels(y_test, y_pred)
print(classification_report(y_test, y_pred, labels=labels_present, target_names=[str(l) for l in labels_present]))


# === Save Model & Encoder
joblib.dump(clf, MODEL_FILE)
joblib.dump(ticker_encoder, ENCODER_FILE)

print(f"\n✅ Model saved: {MODEL_FILE}")
print(f"✅ Encoder saved: {ENCODER_FILE}")
