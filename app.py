from flask import Flask
from database.connection import db
from utils.config import BaseConfig
from flask_migrate import Migrate
from encriptador import bcrypt
from flask_cors import CORS
from api.login import login

app = Flask(__name__)
app.register_blueprint(login)
app.config.from_object(BaseConfig)
CORS(app)
bcrypt.init_app(app)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)
