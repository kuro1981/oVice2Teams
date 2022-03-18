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

    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")
    if name:
        headers={
            "Content-Type": "application/json",
            }
        req = requests.post(
            TEAMS_WEBHOOK_URL,
            headers = headers,
            data = json.dumps(make_message(name, message))
            )
        
        if req.status_code == 200:

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
                "This HTTP trigger had an error.",
                status_code=500,
            )

    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
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
