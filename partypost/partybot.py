from .database import Person, Page, Image
from .facebook.message import *
from . import facebook

ADMIN_CONFIGURED = False
ADMIN_SENDER_ID = os.environ.get("ADMIN_SENDER_ID")
ADMIN_SENDER = Person(ADMIN_SENDER_ID)
ADMIN_PAGE_ACCESS_TOKEN = os.environ.get("ADMIN_PAGE_ACCESS_TOKEN")
if ADMIN_SENDER_ID is not None and ADMIN_PAGE_ACCESS_TOKEN is not None:
    ADMIN_PAGE = Page(access_token=ADMIN_PAGE_ACCESS_TOKEN)
    ADMIN_CONFIGURED = True


DISABLED = os.environ.get("DISABLED", 0) == '1'
MAX_MESSAGE_LENGTH = 600


class Chatbot(object):
    def __init__(self):
        pass

    def receivedMessage(self, senderId, pageId, message, attachments):
        log("Received message \"{}\" from {} on {}".format(message, senderId, pageId))

        page = Page.findById(pageId)
        if page is None:
            log("Error: received message on unregistered page")
            return

        sender = Person.findById(senderId)
        if not sender:
            sender = Person(senderId)
            sender.first_name, sender.last_name = facebook.profile.getName(senderId, page)
            sender.page = page
            sender.add()

        if DISABLED:
            response = TextMessage("I am temporarily offline. Follow the page for updates!")
            response.send(sender, page)
            if len(message) > 5 and ADMIN_CONFIGURED:
                report = TextMessage("{}:\n\"{}\"".format(sender.id, message))
                report.send(ADMIN_SENDER, page)
            return

        self.onMessage(sender, page, message, attachments)

    def onMessage(self, sender, page, message, attachments):
        pass

    def receivedPostback(self, senderId, pageId, payload):
        log("Received postback with payload \"{}\" from {} on {}".format(payload, senderId, pageId))

        page = Page.findById(pageId)
        if page is None:
            log("Error: received message on unregistered page")
            return

        sender = Person.findById(senderId)
        if not sender:
            sender = Person(senderId)
            sender.first_name, sender.last_name = facebook.profile.getName(senderId, page)
            sender.page = page
            sender.add()

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
    def onMessage(self, sender, page, message, attachments):
        msg = TextMessage("Hello there.")
        msg.send(sender, page)
        for attachment in attachments:
            self.processAttachment(sender, page, attachment)

    def processAttachment(self, sender, page, attachment):
        if attachment.media_type == "image":
            image = Image()
            image.sender = sender
            image.page = page
            image.fb_attachment_url = attachment.url
            image.fb_photo_id = facebook.page.postImage(attachment.url, page)
            image.add()
        else:
            log("Unknown attachment type: {}".format(attachment.media_type))

    @postback
    def sendWelcome(self, sender, page):
        msg = TextMessage("Hello there.")
        msg.send(sender, page)

    def sendErrorMessage(self, msg):
        if ADMIN_CONFIGURED:
            notification = TextMessage("Error:\t{}".format(msg))
            notification.send(ADMIN_SENDER, ADMIN_PAGE, isResponse=False)

    def exceptionOccured(self, e, pageId=None):
        log("Exception in request.")
        if pageId is not None:
            log("Error with page: " + str(pageId))
        msg = str(e)
        log(msg)
        self.sendErrorMessage(msg)

