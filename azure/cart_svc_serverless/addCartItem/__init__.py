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

    logging.info(body)
    
    if userID != "":
        existing_data = getItems(userID, r)
    else:
        logging.error("Missing User ID from path parameter")
        return func.HttpResponse('Missing UserID from the request', status_code=400)
    
    
    if (existing_data):
        index = 0
        
        num_exist_data = len(existing_data)
        # for item in existing_data:
        #     if(item['itemid']==body['itemid']):
        #         item['quantity'] = int(body['quantity']) + int(item['quantity'])
        #         payload = json.dumps(item)
        #         try:
        #             r.set(userID, payload)
        #         except Exception as e:
        #             logging.error('Error inserting data into redis %s', payload)
        #             return func.HttpResponse(status_code=500)
        #     else:
        #         continue

        while index < num_exist_data:
            if (existing_data[index]['itemid'] == body['itemid']):
                existing_data[index]['quantity'] = int(body['quantity'])+ int(existing_data[index]['quantity'])
                index = num_exist_data + 1
                payload = json.dumps(existing_data)
                try:
                    r.set(userID, payload)
                except Exception as e:
                    logging.error('Error inserting data into redis %s', payload)
                    return func.HttpResponse(status_code=500)
            else:
                index += 1
            
        if index <= num_exist_data:
            existing_data.append(body)
            payload=json.dumps(existing_data)
            try:
                logging.info('Adding data to redis database %s', payload)
                r.set(userID, payload)
            except Exception as e:
                logging.error("Could not insert data into Redis")
    else:
        payload=[]
        payload.append(body)
        logging.info("Adding payload to redis DB %s", payload)
        try:
            r.set(userID, json.dumps(payload))
        except Exception as e:
            logging.info("Error inserting data into redis")

    return func.HttpResponse('POST method for add item to cart was triggered', status_code=200)

