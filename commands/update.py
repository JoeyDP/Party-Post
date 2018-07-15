import bacli
from util import log

from partypost.database import Page, Image


bacli.setDescription("Commands for updating database")


def run():
    """ Runs cleanup followed by crawl. """
    log("Started update")
    cleanup()
    crawl()
    log("Finished update")


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


def crawl():
    """ Crawls every page for new images that may have been posted. """
    log("Running crawl")
    for page in Page.all():
        pass
        # TODO crawl images on page
        # store in database if not yet present


