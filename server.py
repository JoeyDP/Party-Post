import hmac
import hashlib

import traceback
from flask import request, abort, render_template
from rq.decorators import job

from partypost import app, VERIFY_TOKEN
from util import *
from partypost.partybot import PartyBot
from partypost.facebook.attachment import Attachment

from partypost import redisCon
from partypost.database import Page

partyBot = PartyBot()

CLIENT_SECRET = os.environ['CLIENT_SECRET']

ACCEPTED_MEDIA_TYPES = ["image"]

MESSAGE_LAST_SEQ_KEY = 'message_lastSeq'


@app.route('/messenger', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "", 200


@app.route('/messenger', methods=['POST'])
def webhook():
    """ endpoint for processing incoming messaging events. """
    try:
        if validateRequest(request):
            receivedRequest(request)
        else:
            error = "Invalid request received: " + str(request)
            log(error)
            partyBot.sendErrorMessage(error)
            abort(400)
    except Exception as e:
        partyBot.exceptionOccured(e)
        traceback.print_exc()
        raise e

    return "ok", 200


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def getIndex():
    return "Party Bot!", 200


@app.route('/page/<int:pageId>', methods=['GET'])
def getPage(pageId):
    page = Page.findById(pageId)
    if not page:
        abort(404)

    return render_template('page.html', page=page)


def validateRequest(request):
    advertised = request.headers.get("X-Hub-Signature")
    if advertised is None:
        return False

    advertised = advertised.replace("sha1=", "")
    data = request.get_data()

    received = hmac.new(
        key=CLIENT_SECRET.encode('raw_unicode_escape'),
        msg=data,
        digestmod=hashlib.sha1
    ).hexdigest()

    return hmac.compare_digest(
        advertised,
        received
    )


def receivedRequest(request):
    data = request.get_json()
    debug(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                recipient = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                if messaging_event.get("message"):  # someone sent us a message
                    message = messaging_event["message"].get("text", "")
                    seq = message.get('seq')
                    attachments_data = messaging_event["message"].get("attachments", list())
                    attachments = list()
                    for attachment_data in attachments_data:
                        media_type = attachment_data.get("type")
                        payload = attachment_data.get("payload")
                        if payload:
                            url = payload.get("url")
                            attachment = Attachment(url, media_type)
                            attachments.append(attachment)
                    receivedMessage.delay(sender, recipient, message, attachments, seq)

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    payload = messaging_event["postback"]["payload"]  # the message's text
                    receivedPostback.delay(sender, recipient, payload)


@job('default', connection=redisCon)
def receivedMessage(sender, recipient, message, attachments, seq):
    # filter messages to self
    if sender == recipient:
        return

    # filter duplicates
    lastSeq = redisCon.get(MESSAGE_LAST_SEQ_KEY)
    if seq == lastSeq:
        log("Duplicate message received")
        return

    attachments = [attachment for attachment in attachments if attachment.media_type in ACCEPTED_MEDIA_TYPES]

    try:
        partyBot.receivedMessage(sender, recipient, message, attachments)
        redisCon.set(MESSAGE_LAST_SEQ_KEY, seq, ex=60)
    except Exception as e:
        partyBot.exceptionOccured(e, recipient)
        traceback.print_exc()


@job('default', connection=redisCon)
def receivedPostback(sender, recipient, payload):
    try:
        partyBot.receivedPostback(sender, recipient, payload)
    except Exception as e:
        partyBot.exceptionOccured(e, recipient)
        traceback.print_exc()


