import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("logs.csv")
print(df[df["response_time_ms"]>800])

