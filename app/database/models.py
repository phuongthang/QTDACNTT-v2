import mongoengine as me
from flask_mongoengine import MongoEngine
from mongoengine.fields import StringField, DateField, ListField, IntField, ObjectIdField, EmbeddedDocumentField, ReferenceField, DictField, DateTimeField
from .db import mongoEngine

class Campaign(mongoEngine.Document):
    _id = ObjectIdField()
    name = StringField(required=True)
    description = StringField()
    startTime = DateTimeField(required=True)
    endTime = DateTimeField(required=True)
    keyword = StringField(required=True)
    links = ListField(mongoEngine.StringField())
    total_comments = IntField()
    total_pos = IntField()
    total_neg = IntField()
    total_neu = IntField()
    status = StringField(required=True)

class Comment(mongoEngine.Document):
    _id = ObjectIdField()
    text = StringField(required=True)
    post_id = StringField()
    label = StringField()
    date = DateTimeField()

class Post(mongoEngine.Document):
    _id = ObjectIdField()
    post_id = StringField()
    campaign = StringField()
    source = StringField()
    date = DateField()
    comments = DictField()
    url = StringField()
    text = StringField()
    total_comments = IntField()
    total_pos = IntField()
    total_neg = IntField()
    total_neu = IntField()
    reactions = IntField()
    like = IntField()
    love = IntField()
    haha = IntField()
    wow = IntField()
    sad = IntField()
    care = IntField()
    angry = IntField()