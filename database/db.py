from flask_mongoengine import MongoEngine
#Load db
mongoEngine = MongoEngine()

def initialize_db(app):
    mongoEngine.init_app(app)