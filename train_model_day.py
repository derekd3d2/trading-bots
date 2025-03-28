import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# === Load Labeled Trade Data ===
df = pd.read_csv("day_trade_labels.csv")

# === Encode Labels (WIN, LOSS, NEUTRAL → 2, 0, 1) ===
label_map = {"WIN": 2, "NEUTRAL": 1, "LOSS": 0}
df["label_encoded"] = df["label"].map(label_map)

# === Encode Ticker Symbol (one-hot or label encoding) ===
ticker_encoder = LabelEncoder()
df["ticker_encoded"] = ticker_encoder.fit_transform(df["ticker"])

# === Feature Engineering ===
features = df[["ticker_encoded", "entry_price", "exit_price", "pct_change"]]
labels = df["label_encoded"]

# === Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# === Train Random Forest Classifier ===
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# === Evaluate Model ===
y_pred = clf.predict(X_test)
print("\n📊 Model Evaluation:")
print(classification_report(y_test, y_pred, target_names=["LOSS", "NEUTRAL", "WIN"]))

# === Save Model and Ticker Encoder ===
joblib.dump(clf, "day_trade_model.pkl")
joblib.dump(ticker_encoder, "day_ticker_encoder.pkl")
print("\n✅ Model saved to day_trade_model.pkl")
