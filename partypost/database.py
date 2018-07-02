import datetime
from partypost import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.String(128), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, sender_id=None):
        if sender_id is not None:
            self.id = sender_id

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @staticmethod
    def findById(sender_id):
        person = Person.query.filter_by(id=sender_id).one_or_none()
        return person

    def add(self):
        db.session.add(self)

    def __str__(self):
        return "{} ({})".format(str(self.name), str(self.id))


class Page(db.Model):
    __tablename__ = "page"

    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(512))
    access_token = db.Column(db.String(255))

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, access_token=None):
        super().__init__()
        self.access_token = access_token

    @staticmethod
    def findById(pageId):
        page = Page.query.filter_by(id=pageId).one_or_none()
        return page

    def add(self):
        db.session.add(self)

    def __str__(self):
        return str(self.id)


class Image(db.Model):
    __tablename__ = "image"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_photo_id = db.Column(db.String(128))
    fb_attachment_url = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(512), unique=True)

    sender = db.Column(db.String(128), db.ForeignKey(Person.id))

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, access_token=None):
        super().__init__()
        self.access_token = access_token

    @staticmethod
    def findById(imageId):
        image = Image.query.filter_by(id=imageId).one_or_none()
        return image

    def add(self):
        db.session.add(self)

    def __str__(self):
        return str(self.id)



db.create_all()
