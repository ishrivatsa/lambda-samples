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

## Get data from the redis db
def getItems(id, r):
    if r.exists(id):
        data = json.loads(r.get(id))
        logging.info("Received data")
        logging.info(data)
    else:
        data = 0
    return data


## Request POST /cart/item/add/{userid}
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('getCartTotal was triggered')

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
    
    if userID != "":
        existing_data = getItems(userID, r)
    else:
        logging.error("Missing User ID from path parameter")
        return func.HttpResponse('Missing UserID from the request', status_code=400)

    total = 0

    if (existing_data):
        for items in existing_data:
            quantity = items['quantity']
            price = items['price']
            total += (float(quantity)*float(price))
        
        response = {}
        response['userid'] = userID
        response['carttotal']=total
        response = json.dumps(response)

        logging.info("The total for user %s is %f", userID, total)
    
    else:
        logging.info('No items found in cart')
        return func.HttpResponse('No items found in cart', status_code=204)

    return func.HttpResponse(response, status_code=200)

