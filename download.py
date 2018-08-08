import urllib.request
import zipfile
from tqdm import tqdm

import bacli
from partypost.database import Page
from util import log

bacli.setDescription("Download all images from a page as a zip.")

FORMATS = ['.jpg', '.png']


@bacli.command
def run(pageId: int):
    page = Page.findById(pageId)
    if not page:
        log("No page found with id: {}".format(str(pageId)))
        return

    with open("images_{}.zip".format(page.id), 'wb') as file:
        zip = zipfile.ZipFile(file, 'w')
        for index, image in enumerate(tqdm(page.images)):
            tqdm.write(image.url)
            [format] = [f for f in FORMATS if f in image.url]
            with urllib.request.urlopen(image.url) as response:
                data = response.read()
                zip.writestr('image_{:0=3d}{}'.format(index, format), data)
        zip.close()

