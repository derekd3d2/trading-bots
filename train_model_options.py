import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# === Load Labeled Option Trades ===
df = pd.read_csv("option_trade_labels.csv")

# === Encode Label (WIN, LOSS, NEUTRAL) ===
label_map = {"WIN": 2, "NEUTRAL": 1, "LOSS": 0}
df["label_encoded"] = df["label"].map(label_map)

# === Encode Categorical Fields ===
ticker_encoder = LabelEncoder()
df["ticker_encoded"] = ticker_encoder.fit_transform(df["ticker"])

option_type_encoder = LabelEncoder()
df["option_type_encoded"] = option_type_encoder.fit_transform(df["option_type"])

# === Features and Labels ===
features = df[["ticker_encoded", "option_type_encoded", "entry_price", "future_price", "pct_change"]]
labels = df["label_encoded"]

# === Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# === Train Model ===
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# === Evaluate ===
y_pred = clf.predict(X_test)
print("\n📊 Model Evaluation:")
print(classification_report(y_test, y_pred, target_names=["LOSS", "NEUTRAL", "WIN"]))

# === Save Model & Encoders ===
joblib.dump(clf, "option_trade_model.pkl")
joblib.dump(ticker_encoder, "option_ticker_encoder.pkl")
joblib.dump(option_type_encoder, "option_type_encoder.pkl")
print("\n✅ Saved model and encoders.")
