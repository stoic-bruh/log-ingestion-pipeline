import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
df = pd.read_csv("logs.csv")
features = df[[
    "response_time_ms",
    "status_code"
]]

# Encode service_name
features = pd.get_dummies(df[[
    "response_time_ms",
    "status_code",
    "service_name"
]])

model = IsolationForest(
        contamination=0.1,
        random_state=42
)

model.fit(features)
df["anomaly"]=model.predict(features)
print(df["anomaly"].value_counts())
anomalies = df[df["anomaly"] == -1]
print(anomalies.head())
print(len(anomalies))

normal = df[df["anomaly"] == 1]
anomaly = df[df["anomaly"] == -1]
print(anomaly[anomaly["response_time_ms"] > 800].shape)
print(anomaly[anomaly["status_code"] >= 500].shape)


