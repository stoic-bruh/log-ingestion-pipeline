import redis
from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from datetime import datetime
import logging
import time
import json

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)



def push_to_redis_with_retry(redis_client, key, value, max_retries=3):
    delay = 0.5

    for attempt in range(1, max_retries + 1):
        try:
            redis_client.lpush(key, value)
            return True
        except Exception as e:
            logger.error(
                f"Redis push failed (attempt {attempt}/{max_retries}): {e}"
            )
            if attempt == max_retries:
                break
            time.sleep(delay)
            delay *= 2  # exponential backoff

    return False
    
def write_to_backup(log_data, reason):
    with open("logs_backup.txt", "a") as f:
        f.write(
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "log": log_data
            }) + "\n"
        )

app = FastAPI()
logger.info("API server started")
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation failed for request {request.url}: {exc.errors()}"
    )

    cleaned_errors = [
        {
            "field": " -> ".join(map(str, err["loc"])),
            "message": err["msg"]
        }
        for err in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_failed",
            "details": cleaned_errors
        }
    )



r = redis.Redis(host="localhost", port=6379, decode_responses=True)
class Log(BaseModel):
    timestamp: str
    level: str
    message: str
    service_name: str
    endpoint: str
    response_time_ms: int
    status_code: int
    @field_validator("timestamp")
    def validate_timestamp(cls, value):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("timestamp must be in ISO 8601 format")
        return value
    
    @field_validator("level")
    def validate_level(cls, value):
        value = value.upper()

        if value not in ALLOWED_LEVELS:
            raise ValueError(
                f"level must be one of {', '.join(ALLOWED_LEVELS)}"
            )

        return value
    
    @field_validator("message")
    def validate_message(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("message cannot be empty")

        if len(value) > 1000:
            raise ValueError("message cannot exceed 1000 characters")

        return value

    @field_validator("service_name")
    def validate_service_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("service_name cannot be empty")

        if len(value) > 100:
            raise ValueError("service_name cannot exceed 1000 characters")

        return value

    @field_validator("endpoint")
    def validate_endpoint(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("endpoint cannot be empty")

        if len(value) > 100:
            raise ValueError("endpoint cannot exceed 1000 characters")

        return value

    @field_validator("status_code")
    def validate_status_code(cls, value):

        if  value == None:
            raise ValueError("status_code cannot be empty")

        if value < 100 or value > 599:
            raise ValueError("status_code cannot exceed the range")

        return value

    @field_validator("response_time_ms")
    def validate_response_time_ms(cls, value):
        

        if  value == None:
            raise ValueError("response_time cannot be empty")

        if value < 0:
            raise ValueError("response_time cannot be negative")

        return value

@app.get("/health")
def health():
    return{"status":"ok"} 


@app.post("/logs")
def receive_log(log: Log):
    logger.info(f"Received log: level={log.level} endpoint={log.endpoint} status_code={log.status_code} service={log.service_name} response_Time={log.response_time_ms}")

    success = push_to_redis_with_retry(r, "logs", log.model_dump_json())

    if not success:
        logger.error("All Redis retries failed. Writing to backup file.")
        write_to_backup(log.model_dump(), "redis_unavailable")

        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "message": "Log stored in backup. Redis unavailable."
            }
        )

    logger.info("Pushed log to Redis queue")
    return {"status": "queued"}
