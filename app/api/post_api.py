from app import app
from flask import Flask, jsonify, request, Response, Blueprint
from app.database import models

post = Blueprint('post', __name__)


@post.route("/post")
def get_posts_of_campaign():
    post_id = request.args.get('post_id')
    if post_id is None or not post_id:
        campaign_name = request.args.get('campaign')
        posts = models.Post.objects(campaign=campaign_name)
        if not posts:
            return "No posts found", 404
        return jsonify(posts), 200
    posts = models.Post.objects(post_id=post_id)
    if not posts or posts is None:
        return "Post not found !", 404
    return jsonify({'posts':posts}), 200
