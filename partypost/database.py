import datetime
from partypost import db
from sqlalchemy import ForeignKey, UniqueConstraint


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(255))

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, sender_id=None):
        if sender_id is not None:
            self.id = sender_id
            db.session.add(self)

    def __str__(self):
        return "{} ({})".format(str(self.name), str(self.id))


class Page(db.Model):
    __tablename__ = "page"

    id = db.Column(db.String(128), primary_key=True)
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

    def __str__(self):
        return str(self.id)




db.create_all()
