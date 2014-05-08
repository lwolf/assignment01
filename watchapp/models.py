# coding: utf-8
from datetime import datetime
from watchapp.extensions import db


class File(db.Model):
    STATUS_NORMAL, STATUS_DELETED, STATUS_MISSING = range(0, 3)

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String)
    path = db.Column(db.String, unique=True)
    mimetype = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now())
    status = db.Column(db.Integer, default=STATUS_NORMAL)

    meta = db.relationship('Metadata', backref='file', lazy='dynamic')

    def is_image(self):
        if self.mimetype and self.mimetype.startswith('image'):
            return True
        return False


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    info_id = db.Column(db.Integer, db.ForeignKey('field.id'))
    content = db.Column(db.UnicodeText)


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.UnicodeText)
