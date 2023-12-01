from flask import Flask
from database.connection import db
from utils.config import BaseConfig
from flask_migrate import Migrate
from encriptador import bcrypt
from flask_cors import CORS
from api.login import login
from api.crypto import crypto
from api.user import user_profile
app = Flask(__name__)
app.register_blueprint(login)
app.register_blueprint(crypto)
app.register_blueprint(user_profile)
app.config.from_object(BaseConfig)
CORS(app)
bcrypt.init_app(app)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)
