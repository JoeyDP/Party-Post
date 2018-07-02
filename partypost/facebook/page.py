

import requests
from urllib.parse import urljoin
from util import log


BASE_URL = "https://graph.facebook.com"


def postImage(imageUrl, page):
    url = urljoin(BASE_URL, str(page.id), 'photos')
    params = {
        'access_token': page.access_token,
        'url': imageUrl
    }

    r = requests.post(url, params=params)
    if r.status_code == 200:
        data = r.json()
        return data.get("id")
    else:
        log("Failed to upload image to page {}".format(page.id))
        return None

