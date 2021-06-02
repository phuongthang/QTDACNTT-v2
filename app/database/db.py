from flask_mongoengine import MongoEngine

mongoEngine = MongoEngine()

def initialize_db(app):
    mongoEngine.init_app(app)