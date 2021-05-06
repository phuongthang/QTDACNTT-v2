from app import app
from flask import Flask, jsonify, request, Response, Blueprint
from app.database import models, db
from app.services import main_service

from datetime import datetime
import time
import threading

comment = Blueprint('comment', __name__)


@comment.route("/comment")
def get_comment_of_campaign():
    campaign_name = request.args.get('campaign')
    if campaign_name is None or not campaign_name:
        post_id = request.args.get('post_id')
        if not post_id or post_id is None:
            return "No comments found", 404
        comments = main_service.get_comment_of_post(post_id)
        if not comments:
            return "No comments found", 404
        return jsonify({'comments':comments}), 200
    comments = main_service.get_comments_of_campaign(campaign_name)
    if not comments:
        return "No comments found", 404
    return jsonify({'comments':comments}), 200
