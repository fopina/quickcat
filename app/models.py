from flask_mongoengine import MongoEngine
from mongoengine import errors  # noqa: for other imports
from . import app

db = MongoEngine(app)


class Image(db.Document):
    url = db.StringField(required=True, unique=True)
    reviews = db.IntField()
    category_votes = db.DynamicField()

    meta = {
        'indexes': [
            'url',
            'reviews',
        ]
    }


class Category(db.Document):
	name = db.StringField(required=True, unique=True)