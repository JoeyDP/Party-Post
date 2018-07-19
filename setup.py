import bacli
import partypost.facebook.chat_profile as profile
from partypost.database import Page
from util import log

bacli.setDescription("Run setup for the chatbot of a specific page.")


@bacli.command
def run(pageId: int):
    page = Page.findById(pageId)
    if not page:
        log("No page found with id: {}".format(str(pageId)))
        return
    profile.setup(page)
