from .database import Person, Page
from .facebook.message import *

ADMIN_CONFIGURED = False
ADMIN_SENDER_ID = os.environ.get("ADMIN_SENDER_ID")
ADMIN_PAGE_ACCESS_TOKEN = os.environ.get("ADMIN_PAGE_ACCESS_TOKEN")
if ADMIN_SENDER_ID is not None and ADMIN_PAGE_ACCESS_TOKEN is not None:
    ADMIN_PAGE = Page(access_token=ADMIN_PAGE_ACCESS_TOKEN)
    ADMIN_CONFIGURED = True


DISABLED = os.environ.get("DISABLED", 0) == '1'
MAX_MESSAGE_LENGTH = 600


class Chatbot(object):
    def __init__(self):
        pass

    def receivedMessage(self, senderId, pageId, message):
        log("Received message \"{}\" from {} on {}".format(message, senderId, pageId))

        sender = senderId
        page = Page.findById(pageId)

        if page is None:
            log("Error: received message on unregistered page")
            return

        if ADMIN_CONFIGURED and senderId == ADMIN_SENDER_ID:
            if self.adminMessage(sender, page, message):
                return

        if DISABLED:
            response = TextMessage("I am temporarily offline. Follow the page for updates!")
            response.send(sender, page)
            if len(message) > 5 and ADMIN_CONFIGURED:
                report = TextMessage("{}:\n\"{}\"".format(sender, message))
                report.send(ADMIN_SENDER_ID, page)
            return

        self.onMessage(sender, page, message)

    def onMessage(self, sender, page, message):
        pass

    def receivedPostback(self, sender, page, payload):
        log("Received postback with payload \"{}\" from {}".format(payload, sender))

        if DISABLED:
            response = TextMessage("I am temporarily offline. Follow the page for updates!")
            response.send(sender, page)
            return

        data = json.loads(payload)
        type = data.get("type")
        if not type:
            raise RuntimeError("No 'type' included in postback.")

        if type == "action":
            action = data["action"]
            pb = self.__getattribute__(action)
            log(pb)
            args = data.get("args", dict())
            if not pb:
                raise RuntimeError("No postback for action '{}'.".format(action))
            pb.func(self, sender, **args)

    def adminMessage(self, sender, page, message):
        # TODO: create @command decorator
        if message == "setup":
            return self.runSetup(sender, page, message)

        return False

    def runSetup(self, sender, page, message):
        response = TextMessage("Running setup")
        response.send(sender, page)
        chat_profile.setup(page)
        return True


class postback:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        action = self.func.__name__
        payload = {
            "type": "action",
            "action": action,
        }
        if len(kwargs) > 0:
            payload["args"] = kwargs
        return payload


class PartyBot(Chatbot):
    def onMessage(self, sender, page, message):
        msg = TextMessage("Hello there.")
        msg.send(sender, page)

    @postback
    def sendWelcome(self, sender, page):
        msg = TextMessage("Hello there.")
        msg.send(sender, page)

    def exceptionOccured(self, e, pageId=None):
        log("Exception in request.")
        if pageId is not None:
            log("Error with page: " + str(pageId))
        log(str(e))
        if ADMIN_CONFIGURED:
            notification = TextMessage("Exception:\t{}".format(str(e)))
            notification.send(ADMIN_SENDER_ID, ADMIN_PAGE, isResponse=False)



from .facebook import chat_profile
