import bacli
from util import log


bacli.setDescription("Commands for updating database")


def run():
    """ Runs cleanup followed by crawl. """
    log("Running update")
    cleanup()
    crawl()


def cleanup():
    """ Checks for all images whether they still exist on Facebook. Otherwise they are removed. """
    log("Running cleanup")


def crawl():
    """ Crawls every page for new images that may have been posted. """
    log("Running crawl")


