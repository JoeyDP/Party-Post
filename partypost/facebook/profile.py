import requests
from urllib.parse import urljoin
from util import log


BASE_URL = "https://graph.facebook.com"


def getProfile(sender_id, access_token):
    url = urljoin(BASE_URL, str(sender_id))
    fields = ["first_name", "last_name"]
    params = {
        'access_token': access_token,
        'fields': ','.join(fields)
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        log("Failed to query profile for {}".format(sender_id))
        log(str(r))
        log(r.text)
        return None


def getName(sender_id, page):
    data = getProfile(sender_id, page.access_token)
    if not data:
        raise RuntimeError

    firstName = data.get("first_name")
    lastName = data.get("last_name")
    return firstName, lastName
