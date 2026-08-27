import json
import os
import random
import socket
from flask import Flask, render_template_string, request, make_response, g
import redis

app = Flask(__name__)

option_a = os.getenv("OPTION_A", "Cats")
option_b = os.getenv("OPTION_B", "Dogs")
hostname = socket.gethostname()


def get_redis():
    if not hasattr(g, "redis"):
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        g.redis = redis.Redis(host=redis_host, port=redis_port, socket_timeout=5)
    return g.redis


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ option_a }} vs {{ option_b }}!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
      .button { padding: 15px 30px; font-size: 18px; margin: 10px; cursor: pointer; border: none; border-radius: 5px; color: white; }
      .button-a { background-color: #2b78e4; }
      .button-b { background-color: #e42b2b; }
    </style>
  </head>
  <body>
    <h1>Voting App</h1>
    <form id="choice" name='form' method="POST" action="/">
      <button type="submit" name="vote" value="a" class="button button-a">{{ option_a }}</button>
      <button type="submit" name="vote" value="b" class="button button-b">{{ option_b }}</button>
    </form>
    <p>Processed by host {{ hostname }}</p>
  </body>
</html>
"""


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/", methods=["GET", "POST"])
def index():
    voter_id = request.cookies.get("voter_id")
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:]

    vote = None
    if request.method == "POST":
        redis_conn = get_redis()
        vote = request.form.get("vote")
        data = json.dumps({"voter_id": voter_id, "vote": vote})
        redis_conn.rpush("votes", data)

    resp = make_response(
        render_template_string(
            HTML_TEMPLATE,
            option_a=option_a,
            option_b=option_b,
            hostname=hostname,
            vote=vote,
        )
    )
    resp.set_cookie("voter_id", voter_id)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
