from flask import Flask, render_template, Blueprint
from app.api.campaign_api import campaign
from app.api.comment_api import comment
from app.api.predict_api import predict
from app.api.post_api import post
from app.database import db
from app.services import main_service
from app.services.facebook import fb


app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"db": "devc", "host": "localhost", "port": 27017}
app.register_blueprint(predict)
app.register_blueprint(campaign)
app.register_blueprint(comment)
app.register_blueprint(post)
app.register_blueprint(fb)

db.initialize_db(app)
model = main_service.init_model()


@app.route("/")
def index():
    return render_template("authen/login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/show")
def show():
    return render_template("campaign/index.html")

@app.route("/create")
def create():
    return render_template("campaign/create.html")


@app.route("/detail")
def detail():
    return render_template("campaign/detail.html")

@app.route("/comments")
def comments():
    return render_template("campaign/comment.html")

@app.route("/predicts")
def predicts():
    return render_template("campaign/predicts.html")


app.run()
