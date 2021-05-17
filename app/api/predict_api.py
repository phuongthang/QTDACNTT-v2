from flask import Blueprint, request
from app.database import models, db
from flask import Flask, jsonify, request, Response
from datetime import datetime
from app.services.main_service import crawl, analyse_campaign, predict_sentiment
from app import app

predict = Blueprint('predict', __name__)


@predict.route('/predict', methods=['POST'])
def predict_sentiment_test():
    data = request.get_json()
    text = data['text']
    return predict_sentiment(app.model ,text)