# import the flask web framework
from flask import Flask
import json
import redis as redis
from flask import Flask, request
from loguru import logger


app = Flask(__name__)

HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    current_engine_temperature = engine_temperature
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    total_temperature = 0

    for i in engine_temperature_values:
        total_temperature += i
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")
    average_engine_temperature = total_temperature/len(engine_temperature_values)

    logger.info(f"record request successful")
    return {"current_engine_temperature": current_engine_temperature,
            "average_engine_tmperature": average_engine_temperature}, 200