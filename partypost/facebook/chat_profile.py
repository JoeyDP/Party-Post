import json
import requests
from util import *
from ..partybot import PartyBot


PROFILE_URL = "https://graph.facebook.com/me/messenger_profile"
HEADERS = {"Content-Type": "application/json"}


def post(data, accessToken):
    jsonData = json.dumps(data)
    r = requests.post(PROFILE_URL, params={"access_token": accessToken}, headers=HEADERS, data=jsonData)
    if r.status_code != 200:
        log("error: {}".format(str(r.status_code)))
    log(r.text)


def setup(page):
    log("setting up profile")
    startButton = getStartedButtonData()
    welcome = getWelcomeData()
    menu = getMenuData()

    data = {**startButton, **welcome, **menu}
    log(data)
    post(data, page.access_token)


def getStartedButtonData():
    data = {
        "get_started": {
            "payload": json.dumps(PartyBot.sendWelcome())
        }
    }
    return data


def getWelcomeData():
    data = {"greeting": [
        {
            "locale": "default",
            "text": "Let's get this party started!"
        }
        ]
    }

    return data


def getMenuData():
    # menu = {
    #     "locale": "default",
    #     "composer_input_disabled": False,
    #     "call_to_actions": [
    #
    #     ],
    # }
    #
    # data = {
    #     "persistent_menu": [menu]
    # }
    data = dict()
    return data


