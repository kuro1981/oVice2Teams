import logging
from urllib import request

import azure.functions as func
from . import settings
import json

import requests

TEAMS_WEBHOOK_URL = ''
TEAMS_EMAIL = ''
TEAMS_USER_NAME = ''

def main(req: func.HttpRequest) -> func.HttpResponse:
    global TEAMS_WEBHOOK_URL
    global TEAMS_EMAIL
    global TEAMS_USER_NAME
    logging.info("Python HTTP trigger function processed a request.")


    if settings.ALL_HOOK:
        TEAMS_WEBHOOK_URL = req.params.get("TEAMSHOOKURL")
        TEAMS_EMAIL = req.params.get("TEAMSEMAIL")
        TEAMS_USER_NAME = req.params.get("USERNAME")
    
    else:
        TEAMS_WEBHOOK_URL = settings.TEAMS_WEBHOOK_URL
        TEAMS_EMAIL = settings.USER_EMAIL
        TEAMS_USER_NAME = settings.USER_NAME

    name = req.params.get("name")
    message = req.params.get("message")

    logging.info(f"request detail is below")
    logging.info(f"name : {name}")
    logging.info(f"message : {message}")
    logging.info(f"TEAMS_WEBHOOK_URL : {TEAMS_WEBHOOK_URL}")
    logging.info(f"TEAMS_EMAIL : {TEAMS_EMAIL}")
    logging.info(f"TEAMS_USER_NAME : {TEAMS_USER_NAME}")

    headers={
        "Content-Type": "application/json",
        }
    req = requests.post(
        TEAMS_WEBHOOK_URL,
        headers = headers,
        data = json.dumps(make_message(name, message))
        )
    
    if req.status_code == 200:

        logging.info(f"POST execution sucessed.")

        return func.HttpResponse(
            "This HTTP triggered function executed successfully.",
            status_code=200,
        )

    if req.status_code != 200:
        logging.ERROR(req.params)

        logging.ERROR(f"TEAMS_WEBHOOK_URL = {TEAMS_WEBHOOK_URL}")
        logging.ERROR(f"TEAMS_EMAIL = {TEAMS_EMAIL}")
        logging.ERROR(f"TEAMS_USER_NAME = {TEAMS_USER_NAME}")

        return func.HttpResponse(
            "This HTTP POST data had an error, but request executed successfully.",
            status_code=200,
        )



def make_message(name, message):
    global TEAMS_EMAIL
    global TEAMS_USER_NAME
    data = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": "oViceで" + name + "さんからメンションが来ました。",
                        },
                        {"type": "TextBlock", "text": "Hi <at>USER_EMAIL</at>"},
                        {"type": "TextBlock", "text": message},
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.0",
                    "msteams": {
                        "entities": [
                            {
                                "type": "mention",
                                "text": "<at>USER_EMAIL</at>",
                                "mentioned": {
                                    "id": TEAMS_EMAIL,
                                    "name": TEAMS_USER_NAME,
                                },
                            }
                        ]
                    },
                },
            }
        ],
    }

    return data
