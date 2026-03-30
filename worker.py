import redis
import time
from datetime import datetime
import logging
import json
import psycopg2
import csv
import os
from psycopg2.extras import execute_values
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

total_processed = 0
total_failed = 0
start_time = time.time()
window_processed = 0
window_failed = 0
window_starttime = time.time()
buffer = []
last_flush_time = time.time()
logger = logging.getLogger(__name__)
logger.info("Worker started, monitoring Redis queue")
max_buffer_size = 1000
max_redis_queue_size = 10000
def connect_to_redis():
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    try:
        if client.ping():
            return client 
    except:
        logger.warning("Redis down, retrying")
        return None

def connect_to_db():
    try:
        db = psycopg2.connect(dbname = "logs_db",user = "postgres",password = "postgres",host = "localhost",port = 5432)
        return db
    except:
        logger.warning("database down")
        return None
            
r = connect_to_redis()
db = connect_to_db()




while True:
    if len(buffer)>=max_buffer_size:
        logger.warning("max buffer size exceeded,going to sleep")
        logger.warning("system under pressure")
        time.sleep(2)
    elif r and r.llen("logs")>=max_redis_queue_size:
        logger.warning("SYSTEM OVERLOADED — Redis backlog growing")
        time.sleep(3)
    elif not r:
        r = connect_to_redis()
        if not r:
            time.sleep(5)
    else:
        try:
            log = r.rpop("logs")
            if log:
                total_processed +=1
                if total_processed % 50 == 0:
                    window_processed=0
                    window_failed=0
                    window_starttime=time.time()
                window_processed+=1
                try:
                    data = json.loads(log)

                    required_fields = ["timestamp", "service_name", "endpoint", "response_time_ms", "status_code", "level", "message"]

                    if not all(field in data for field in required_fields):
                        bad_data = log[:200]
                        timestamp = datetime.now().isoformat()
                        logger.warning("Missing required fields in log")
                        with open("dead_letter.txt", "a") as f:
                            f.write(f"[{timestamp}] MISSING_FIELDS: {bad_data}\n")
                        total_failed +=1
                        window_failed+=1
                        continue

                except  json.JSONDecodeError:
                    bad_data = log[:200]
                    logger.warning("Invalid JSON received from Redis")
                    timestamp = datetime.now().isoformat()
                    with open("dead_letter.txt", "a") as f:
                        f.write(f"[{timestamp}] JSON_ERROR: {bad_data}\n")
                    total_failed +=1
                    window_failed+=1
                    continue
                logger.info("Pulled log from Redis queue")
                timestamp = datetime.now().isoformat()
                buffer.append((data["timestamp"], data["service_name"], data["endpoint"], data["response_time_ms"], data["status_code"], data["level"], data["message"]))
                if db is None:
                    db = connect_to_db()
                    if db is None:
                        with open("logs.txt", "a")  as f:
                            for i in buffer:
                                f.write(f'[{i[0]}]{i[1]}:{i[2]}\n')
                    
                        buffer=[]
                        last_flush_time = time.time()
                    continue
                try:
                    if (len(buffer)>=10 or time.time()-last_flush_time>=5) and buffer!=[]:
                        cursor = db.cursor()
                        query = "insert into logs(timestamp,service_name,endpoint,response_time_ms,status_code,level,message)values %s"
                        execute_values(cursor,query,buffer)
                        db.commit()
                        cursor.close()
                        logger.info(f'Saved {len(buffer)} logs to db successfully')
                        file_exists = False

                        try:
                            file_exists = open("logs.csv").close() is None
                        except:
                            file_exists = False

                        with open("logs.csv", mode="a", newline="") as file:
                            writer = csv.writer(file)

                            if not file_exists:
                                writer.writerow([
                                    "timestamp",
                                    "service_name",
                                    "endpoint",
                                    "response_time_ms",
                                    "status_code",
                                    "level",
                                    "message"
                                ])

                            writer.writerows(buffer)
                        buffer = []
                        last_flush_time = time.time()
                except Exception as e:
                    db = None
                    with open("logs.txt", "a")  as f:
                        for i in buffer:
                            f.write(f'[{i[0]}]{i[1]}:{i[2]}\n')
                    buffer=[]
                    last_flush_time = time.time()
                    logger.error(e)
                

                
                if total_processed % 50 == 0:
                    elapsed_time = time.time() - start_time

                    # Throughput (logs per second)
                    if elapsed_time > 0:
                        throughput = total_processed / elapsed_time
                    else:
                        throughput = 0

                    # Success rate
                    if total_processed > 0:
                        success_rate = ((total_processed - total_failed) / total_processed) * 100
                    else:
                        success_rate = 0

                    # Uptime formatting
                    uptime_seconds = int(elapsed_time)
                    hours = uptime_seconds // 3600
                    minutes = (uptime_seconds % 3600) // 60
                    seconds = uptime_seconds % 60

                    logger.info("------ Worker Stats ------")
                    logger.info(f"Processed: {total_processed}")
                    logger.info(f"Failed: {total_failed}")
                    logger.info(f"Success Rate: {success_rate:.2f}%")
                    logger.info(f"Throughput: {throughput:.2f} logs/sec")
                    logger.info(f"Uptime: {hours}h {minutes}m {seconds}s")
                    logger.info("--------------------------")
            else:
                logger.debug("Queue empty, waiting...")
                time.sleep(0.5)

        except Exception as e:
            logger.warning(f"Worker error (Redis unavailable). Retrying in 2 seconds: {e}")
            time.sleep(5)
            r = None


