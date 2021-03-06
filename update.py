import bacli

from partypost.database import Page, Image
from util import log, debug

from RESTfacebook import FacebookAPI
from RESTfacebook.page import Page as FBPage
from RESTapi import RequestException

from tqdm import tqdm


bacli.setDescription("Commands for updating database")


@bacli.command
def run():
    """ Runs cleanup followed by crawl. """
    log("Started update")
    cleanup()
    crawl()
    log("Finished update")


@bacli.command
def cleanup():
    """ Checks for all images whether they still exist on Facebook. Otherwise they are removed. """
    log("Running cleanup")
    for page in Page.all():
        api = FacebookAPI(page.access_token)
        for image in page.images:
            if image.fb_photo_id:
                try:
                    post = api.getPost(image.fb_photo_id)
                    log("Image with id {} and url {} still good.".format(image.id, image.url))
                except RequestException as e:
                    data = e.request.json()
                    if 'error' in data:
                        error = data['error']
                        if int(error.get('code', 0)) == 100:
                            log("Image with id {} and url {} was removed from Facebook.".format(image.id, image.url))
                            log("Deleting it from the database.")
                            image.delete()
                            log("")


@bacli.command
def crawl():
    """ Crawls every page for new images that may have been posted. """
    log("Running crawl")
    for page in Page.all():
        api = FacebookAPI(page.access_token)
        pageApi = FBPage(api, id=page.id)
        photos = pageApi.getPhotos(type='uploaded', fields='images')
        for photo in tqdm(photos):
            tqdm.write("Processing photo with id {}".format(str(photo.id)), end='\t->\t')
            if Image.findByPhotoId(photo.id):
                # Note: If chronologically, the loop may be stopped here to increase performance.
                tqdm.write("Already present")
            else:
                tqdm.write("Not in database yet, adding it")
                fbImage = _getBestImage(photo.images)

                image = Image()
                image.sender = None
                image.page = page
                image.fb_attachment_url = fbImage.source
                image.fb_photo_id = photo.id
                image.add()


def _getBestImage(images):
    return max(images, key=lambda x: x.width * x.height)
