AI-Powered Log Ingestion and Anomaly Detection Pipeline:
Overview
This project implements a production-style log ingestion pipeline combined with machine learning-based anomaly detection.
It simulates real-world distributed systems where logs are generated, processed asynchronously, stored efficiently, and analyzed for anomalies.

Problem Statement:
Modern systems generate large volumes of logs. Detecting failures, latency spikes, and abnormal behavior manually is inefficient.

This project aims to:
Build a scalable log ingestion system
Ensure fault tolerance and reliability
Apply unsupervised machine learning to detect anomalies


System Architecture
Log Generator → FastAPI → Redis Queue → Worker → PostgreSQL → CSV → ML Model

Components:
FastAPI: Validates and ingests logs
Redis: Acts as a buffer/queue for decoupling
Worker: Processes logs asynchronously with batching
PostgreSQL: Persistent structured storage
CSV Export: Dataset for ML
Isolation Forest: Anomaly detection


Features:

Backend System
Structured logging (ML-ready schema)
Input validation using Pydantic
Retry logic for Redis failures
Backup file handling for fault tolerance

Worker Processing
Batch insertion into database
Backpressure handling
Buffer-based processing
Graceful degradation when database is unavailable

Observability
Throughput tracking
Success/failure metrics
Logging for monitoring and debugging


Dataset

Generated approximately 5000 logs with:
Normal logs (~80%)
Error logs (HTTP 500)
Performance anomalies (response_time > 800ms)
Multiple services (auth, billing, inventory, gateway)


Machine Learning Approach
Model Used
Isolation Forest (Unsupervised Learning)

Features
response_time_ms
status_code
service_name (encoded)

Rationale
Works without labeled data
Efficient for large datasets
Suitable for anomaly detection in log data


Results
Total logs: ~5000
Detected anomalies: ~999 (~20%)
Slow logs detected: ~27%
Strong detection of error (500) logs


Key Insights
Majority of logs are normal (status 200)
Certain services (e.g., inventory-db) show higher failure rates
Response time distribution shows a long tail (latency spikes)
Model performance decreases when anomaly ratio is high


Limitations
High anomaly ratio reduces model effectiveness
Limited feature set (no temporal features)
Simulated data does not capture real-world noise fully
Presence of false positives


Future Improvements
Add time-series features
Use advanced models such as LSTM or Autoencoders
Implement real-time anomaly alerts
Improve feature engineering
Compare multiple anomaly detection models


How to Run
Start Services
docker run -d -p 6379:6379 redis
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=logs_db postgres

Start API
uvicorn api:app --reload

Start Worker
python worker.py

Generate Logs
python generator.py

Run Analysis
python analysis.py
python anomaly.py


What This Project Demonstrates:
Distributed system design
Queue-based architecture
Fault-tolerant backend engineering
Data pipeline construction
Applied machine learning
Analytical thinking and evaluation


Conclusion
This project demonstrates how backend systems and machine learning can be combined to build scalable, reliable pipelines that not only process data but also extract meaningful insights automatically.


