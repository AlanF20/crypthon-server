import jwt
import datetime
from utils.config import BaseConfig
from app import db, bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField
from wtforms.validators import DataRequired, URL
import base64
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    wallet = db.relationship("Wallet", backref="users", lazy=True)
    money_balance = db.Column(db.Float, default=10000.0)

    def __init__(
        self, email, password, first_name=None, last_name=None, admin=False
    ) -> None:
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, BaseConfig.BCRYPT_LOG_ROUNDS
        ).decode()

        self.registered_on = datetime.now()
        self.admin = admin
        self.first_name = first_name if first_name is not None else "Sin asignar"
        self.last_name = last_name if last_name is not None else "Sin asignar"

    def encode_auth_token(self, user_id):
        try:
            print("USER", user_id)
            payload = {
                "iat": datetime.utcnow(),
                "sub": user_id,
            }
            print("PAYLOAD", payload)
            return jwt.encode(payload, BaseConfig.SECRET_KEY, algorithm="HS256")
        except Exception as e:
            print("EXCEPTION")
            print(e)
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, BaseConfig.SECRET_KEY, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            return "Signature Expired Please log in again"

        except jwt.InvalidTokenError as e:
            return "Invalid token"


class CryptoCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptoImg = db.Column(db.Text)
    cryptoName = db.Column(db.String(50), unique=True, nullable=False)
    cryptoPrice = db.Column(db.String(20))
    cryptoSymbol = db.Column(db.String(10), unique=True, nullable=False)
    coinIncrement = db.Column(db.Float)

    def serialize(self):
        return {
            "id": self.id,
            "cryptoImg": self.cryptoImg,
            "cryptoName": self.cryptoName,
            "cryptoPrice": self.cryptoPrice,
            "cryptoSymbol": self.cryptoSymbol,
            "coinIncrement": self.coinIncrement
            if self.coinIncrement is not None
            else None,
        }


class CryptoForm(FlaskForm):
    cryptoImg = FileField("Imagen", validators=[DataRequired()])
    cryptoName = StringField("Nombre", validators=[DataRequired()])
    cryptoPrice = StringField("Precio")
    cryptoSymbol = StringField("Símbolo", validators=[DataRequired()])
    coinIncrement = FloatField("Incremento")

    def encode_image(self):
        if self.cryptoImg.data:
            return base64.b64encode(self.cryptoImg.data.read()).decode("utf-8")
        return None


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    crypto_id = db.Column(
        db.Integer, db.ForeignKey("crypto_currency.id"), nullable=False
    )
    quantity = db.Column(db.Float, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crypto_id": self.crypto_id,
            "quantity": self.quantity,
        }


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    crypto_id = db.Column(
        db.Integer, db.ForeignKey("crypto_currency.id"), nullable=False
    )
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "users_id": self.user_id,
            "crypto_id": self.crypto_id,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
        }
