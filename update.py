import bacli

from partypost.database import Page, Image
from util import log, debug

from RESTfacebook import FacebookAPI
from RESTfacebook.page import Page as FBPage


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
    for image in Image.all():
        # TODO query image
        post = None
        if post is None:
            log("Image with id {} and url {} was removed from Facebook.".format(image.id, image.url))
            log("Deleting it from the database.")
            # image.delete()
            log("")


@bacli.command
def crawl():
    """ Crawls every page for new images that may have been posted. """
    log("Running crawl")
    for page in Page.all():
        api = FacebookAPI(page.access_token)
        pageApi = FBPage(api, id=page.id)
        photos = pageApi.getPhotos(type='uploaded', fields='images')
        for photo in photos:
            debug("Processing photo with id {}".format(str(photo.id)))
            if Image.findByPhotoId(photo.id):
                debug("Already present")
                # Note: If chronologically, the loop may be stopped here to increase performance.
            else:
                debug("Not in database yet, adding it")
                fbImage = _getBestImage(photo.images)

                image = Image()
                image.sender = None
                image.page = page
                image.fb_attachment_url = fbImage.source
                image.fb_photo_id = photo.id
                image.add()


def _getBestImage(images):
    return max(images, key=lambda x: x.width * x.height)
