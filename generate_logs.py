import random
import json
import time
from datetime import datetime
import requests
API_URL = "http://127.0.0.1:8000/logs"


# --- Configuration & Constraints ---
SERVICES = ["auth-service", "billing-api", "inventory-db", "gateway-proxy"]
ENDPOINTS = {
    "auth-service": ["/login", "/logout", "/verify-token"],
    "billing-api": ["/checkout", "/subscription/cancel", "/invoice/download"],
    "inventory-db": ["/products/list", "/stock/update"],
    "gateway-proxy": ["/health", "/metrics"]
}

# Probabilities (weights) to make the data look realistic
LEVELS = ["INFO", "WARNING", "ERROR"]
LEVEL_WEIGHTS = [85, 10, 5]  # 85% INFO, 10% WARNING, 5% ERROR

STATUS_CODES = [200, 201, 400, 401, 404, 500]
STATUS_WEIGHTS = [70, 15, 5, 3, 5, 2] # Mostly 200s/201s

MESSAGES = {
    "INFO": "Request processed successfully",
    "WARNING": "Slow response detected from upstream",
    "ERROR": "Internal connection timeout"
}

def generate_sample_log():
    service = random.choice(SERVICES)
    level = random.choices(LEVELS, weights=LEVEL_WEIGHTS)[0]
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "service_name": service,
        "endpoint": random.choice(ENDPOINTS[service]),
        "response_time_ms": random.randint(10, 1000), # Constraint: float between 10-500ms
        "status_code": random.choices(STATUS_CODES, weights=STATUS_WEIGHTS)[0],
        "message": MESSAGES[level]
    }
    return log_entry

# --- Execution ---
# Generate 5 sample logs and print as JSON
for _ in range(5000):
    log = generate_sample_log()

    try:
        response = requests.post(API_URL, json=log)
        
        if response.status_code != 200:
            print("Failed:", response.text)

    except Exception as e:
        print("Error:", e)

    time.sleep(0.01)  # simulate traffic (100 logs/sec)
