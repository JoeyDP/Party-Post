import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bootstrap import Bootstrap

import redis


DATABASE_URL = os.environ.get('DATABASE_URL')
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
DEBUG = bool(os.environ.get("DEBUG", False))

app = Flask(__name__)
app.debug = DEBUG
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = VERIFY_TOKEN

db = SQLAlchemy(app)

redis_url = os.getenv('REDIS_URL')
redisCon = redis.from_url(redis_url)
