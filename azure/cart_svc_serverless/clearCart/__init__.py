import logging
import os
from os import environ
import redis
import json
import azure.functions as func

redisHost= ""
redisPort = 6379
redisPassword = ""

def connectRedis(host, port, password):
    try:
        logging.info("Connecting to Redis ")
        redisConnection = redis.StrictRedis(host=host, port=port, password=password, db=0)
    except Exception as e:
        logging.error("Error connecting to REDIS %s", e)
        return func.HttpResponse('Could not connect to REDIS', status_code=500)

    try:
        logging.info(redisConnection.ping())
    except Exception as e:
        logging.error("Could not Ping Redis server %s", e)
        return func.HttpResponse('Could not Ping REDIS', status_code=500)

    logging.info("Successfully Connected to Redis")
    return redisConnection


## Request POST /cart/clear/{userid}
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if environ.get("REDIS_HOST") is not None:
        if os.environ["REDIS_HOST"] != "":
            redisHost = os.environ["REDIS_HOST"]
        else:
            logging.info("REDIS_HOST is empty")
            return func.HttpResponse(status_code=500)
    else:
        logging.error("REDIS_HOST is not Set")
        return func.HttpResponse(status_code=500)


    if environ.get("REDIS_PORT") is not None:
        if os.environ["REDIS_PORT"] != "":
           redisPort = os.environ["REDIS_PORT"]
        else:
             redisPort = 6379
    else:
        logging.error("Could not find REDIS_PORT")
        return func.HttpResponse(status_code=500)

    if environ.get("REDIS_PASSWORD") is not None:
        if os.environ["REDIS_PASSWORD"] != "":
           redisPassword = os.environ["REDIS_PASSWORD"]
        else:
            logging.info("REDIS_PASSWORD is empty")
            return func.HttpResponse(status_code=500)
    else:
        logging.error("REDIS_PASSWORD is not Set")
        return func.HttpResponse(status_code=500)

    ## Connect to REDIS

    r = connectRedis(redisHost, redisPort,redisPassword)

    logging.info(req.route_params["userid"])

    userID = req.route_params["userid"]

    try: 
        logging.info("Clearing cart for user %s", userID)
        r.delete(userID)
    except Exception as e:
        logging.error('Could not clear cart %s', e)
        return func.HttpResponse(status_code=400)
    
    return func.HttpResponse(status_code=200)


