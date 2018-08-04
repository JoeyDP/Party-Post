import datetime
from partypost import db

from sqlalchemy.dialects import postgresql

class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.String(128), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    page_id = db.Column(db.String(128), db.ForeignKey("page.id", ondelete='CASCADE', onupdate='CASCADE'))
    page = db.relationship("Page")

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
        person = Person.query.filter_by(id=str(sender_id)).one_or_none()
        return person

    def add(self):
        db.session.add(self)
        db.session.commit()

    def __str__(self):
        return "{} ({})".format(str(self.name), str(self.id))


class Page(db.Model):
    __tablename__ = "page"

    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(512))
    access_token = db.Column(db.String(255))
    fb_post_access_token = db.Column(db.String(255))

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    images = db.relationship("Image", back_populates="page", foreign_keys="Image.page_id")

    info_image_id = db.Column(db.Integer, db.ForeignKey("image.id", ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    info_image = db.relationship("Image", foreign_keys="Page.info_image_id")

    def __init__(self, access_token=None):
        super().__init__()
        self.access_token = access_token

    @property
    def post_access_token(self):
        if self.fb_post_access_token:
            return self.fb_post_access_token
        return self.access_token

    @staticmethod
    def findById(pageId):
        page = Page.query.filter_by(id=str(pageId)).one_or_none()
        return page

    @staticmethod
    def all():
        return Page.query.all()

    def getNewImages(self, minTime=None, maxTime=None, amount=3):
        q = Image.query.filter_by(page=self)
        if self.info_image:
            q = q.filter(Image.id != self.info_image.id)

        images = list()
        # Query newer images
        if maxTime:
            qMax = q.filter(Image.time_created > maxTime).order_by(Image.time_created.asc()).limit(amount)
            images.extend(qMax.all())

        # Query older images
        remaining = amount - len(images)
        if minTime and remaining > 0:
            qMin = q.filter(Image.time_created < minTime).order_by(Image.time_created.desc()).limit(remaining)
            images.extend(qMin.all())
        else:
            q = q.order_by(Image.time_created.desc()).limit(remaining)
            return q.all()

        # If no time specified, query all
        if not minTime and not maxTime:
            q = q.order_by(Image.time_created.desc()).limit(amount)
            images = q.all()

        return images

    def add(self):
        db.session.add(self)
        db.session.commit()

    def __str__(self):
        return str(self.id)


class Image(db.Model):
    __tablename__ = "image"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_photo_id = db.Column(db.String(128))
    fb_attachment_url = db.Column(db.String(255))

    sender_id = db.Column(db.String(128), db.ForeignKey("person.id", ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    sender = db.relationship("Person")

    page_id = db.Column(db.String(128), db.ForeignKey("page.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    page = db.relationship("Page", back_populates="images", foreign_keys="Image.page_id")

    time_created = db.Column(db.DateTime, default=datetime.datetime.now)
    time_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, access_token=None):
        super().__init__()
        self.access_token = access_token

    @staticmethod
    def findById(imageId):
        image = Image.query.filter_by(id=int(imageId)).one_or_none()
        return image

    @staticmethod
    def findByPhotoId(photoId):
        image = Image.query.filter_by(fb_photo_id=str(photoId)).one_or_none()
        return image

    @staticmethod
    def all():
        return Image.query.all()

    @property
    def url(self):
        return self.fb_attachment_url

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return str(self.id)


db.create_all()
