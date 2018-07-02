

import requests
from urllib.parse import urljoin
from util import log


BASE_URL = "https://graph.facebook.com"


def postImage(imageUrl, page):
    url = urljoin(BASE_URL, 'me/photos')
    params = {
        'access_token': page.access_token,
        'url': imageUrl
    }
    log(url)

    r = requests.post(url, params=params)
    if r.status_code == 200:
        data = r.json()
        return data.get("id")
    else:
        log("Failed to upload image to page {}".format(page.id))
        log(str(r))
        log(r.text)
        return None

