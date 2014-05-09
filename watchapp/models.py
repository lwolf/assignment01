# coding: utf-8
from datetime import datetime
from watchapp.extensions import db

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_enum_dict import EnumDictForInt

DeclarativeBase = declarative_base()
DeclarativeBase.query = db.session.query_property()


class File(db.Model):
    STATUS = EnumDictForInt.Enum(
        ('NORMAL', {
            'db': 0,
            'title': 'normal'
        }),
        ('DELETED', {
            'db': 1,
            'title': 'deleted',
        })
    )

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String)
    path = db.Column(db.String, unique=True)
    mimetype = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now())
    status = db.Column(EnumDictForInt(STATUS))

    meta = db.relationship(
        'Metadata',
        backref='file',
        lazy='joined',
        cascade="all,delete"
    )

    def is_image(self):
        if self.mimetype and self.mimetype.startswith('image'):
            return True
        return False


class Metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    info_id = db.Column(db.Integer, db.ForeignKey('field.id'))
    field_info = db.relationship('Field', lazy='joined')
    content = db.Column(db.UnicodeText)


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.UnicodeText)
