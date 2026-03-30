import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("logs_with_anomalies.csv")

# Histogram
plt.hist(df["response_time_ms"], bins=50)
plt.title("Response Time Distribution")
plt.xlabel("Response Time (ms)")
plt.ylabel("Frequency")
plt.show()

# Scatter plot
plt.scatter(df["response_time_ms"], df["status_code"], c=df["anomaly"])
plt.title("Anomaly Detection")
plt.xlabel("Response Time")
plt.ylabel("Status Code")
plt.show()