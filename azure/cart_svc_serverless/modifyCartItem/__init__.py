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


## Request POST /cart/item/modify/{userid}
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

    body = req.get_json()

    logging.info("Body received for modify cart ", body)

    try:
        existing_data=getItems(userID, r)
    except Exception as e:
        logging.error('Could not retrieve cart items')
        return func.HttpResponse(status_code=500)


    if(existing_data):
        index = 0
        while index < len(existing_data):
            ## delete an item from the data
            if (existing_data[index]['itemid'] ==  body['itemid']) and (body['quantity'] == 0):
                del existing_data[index]
                payload = json.dumps(existing_data)
                logging.info("modified payload is %s", payload)
                try:
                    logging.info("Removing item from cart")
                    r.set(userID, payload)
                except Exception as e:
                    logging.error("Could not remove item from cart %s", e)
                    return func.HttpResponse(status_code=500)
                index = len(existing_data)
            elif (existing_data[index]['itemid'] == body['itemid']):
                existing_data[index]['quantity'] = body['quantity']
                payload = json.dumps(existing_data)
                logging.info("modified payload is %s", payload)
                try:
                    logging.info("Updating cart items")
                    r.set(userID, payload)
                except Exception as e:
                    logging.error("Could not update cart items %s", e)
                    return func.HttpResponse(status_code=500)
                index = len(existing_data)
            else:
                index += 1
    else:
        logging.info("No items found in cart for user %s", userID)
        return func.HttpResponse('No items found in cart', status_code=204)
    
    return func.HttpResponse(status_code=200)
