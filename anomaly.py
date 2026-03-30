import pandas as pd
from sklearn.ensemble import IsolationForest

# Load data
df = pd.read_csv("logs.csv")

# Features for ML
features = df[["response_time_ms", "status_code"]]

# Train model
model = IsolationForest(contamination=0.1, random_state=42)
df["anomaly"] = model.fit_predict(features)

# Convert labels
df["anomaly"] = df["anomaly"].map({1: 0, -1: 1})

# Results
total = len(df)
anomalies = df["anomaly"].sum()

print("Total logs:", total)
print("Anomalies detected:", anomalies)
print("Anomaly %:", (anomalies / total) * 100)

# Show some anomalies
print("\nSample anomalies:")
print(df[df["anomaly"] == 1].head())

# Save result
df.to_csv("logs_with_anomalies.csv", index=False)