Log Ingestion Pipeline with ML-based Anomaly Detection
Overview
Modern distributed systems generate massive volumes of logs. Identifying anomalies in these logs is critical for detecting failures, performance issues, and security risks.
This project builds a production-style log ingestion pipeline and explores the use of unsupervised machine learning (Isolation Forest) to detect anomalies in structured log data.

System Architecture
Log Generator → FastAPI → Redis Queue → Worker → PostgreSQL → CSV → ML Analysis

Features:
FastAPI-based log ingestion API
Redis queue for decoupling ingestion and processing
Worker with buffering, retry logic, and fault tolerance
PostgreSQL for persistent storage
CSV export for ML analysis
Isolation Forest for anomaly detection
Basic visualization of log patterns


Dataset Generation:
Synthetic logs generated to simulate distributed systems


Fields included:
timestamp
service_name
endpoint
response_time_ms
status_code
level
message



Total logs generated: 15,000+



Methodology
Extracted numerical features:
response_time_ms
status_code


Applied:
Isolation Forest (unsupervised anomaly detection)



Model configuration:
contamination = 0.1




Results
Total logs: 15,005
Anomalies detected: 1,501
Anomaly rate: ~10%

Key Observations:
The model detected ~10% anomalies, consistent with the contamination parameter
Extreme response times were the primary driver of anomalies
Status codes had limited influence on anomaly detection
The model selected the most "unusual" points rather than discovering true anomalies


Insights:
Isolation Forest requires a predefined anomaly ratio, which may not reflect real-world scenarios
Numerical features dominated anomaly detection behavior
Uniform synthetic data limited meaningful separation between normal and anomalous patterns


Limitations
Synthetic dataset (not real-world logs)
Limited feature set (no request context, user data, etc.)
No temporal or sequence-based analysis
Isolation Forest sensitivity to contamination parameter
Lack of labeled ground truth for evaluation


Future Work:
Use real production log datasets
Add time-series anomaly detection
Feature engineering (log patterns, frequency, sequences)
Compare with other models (LOF, Autoencoders)
Real-time anomaly detection pipeline


How to Run
1. Start services (Docker)
docker start redis
docker start postgres


2. Run API
uvicorn api:app --reload


3. Run worker
python worker.py


4. Generate logs
python generate_logs.py


5. Run anomaly detection
python anomaly.py


6. Run analysis
python analysis.py


Technologies Used:
Python
FastAPI
Redis
PostgreSQL
Pandas
Scikit-learn
Matplotlib


Conclusion
This project demonstrates how a production-style log pipeline can be combined with machine learning to explore anomaly detection. While the system successfully identifies unusual patterns, it also highlights the limitations of unsupervised methods and synthetic data.

Author
GitHub: https://github.com/stoic-bruh/log-ingestion-pipeline
