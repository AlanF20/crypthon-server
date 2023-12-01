from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from models import User
from app import db, bcrypt
from auth import tokenCheck

login = Blueprint("login", __name__)


@login.route("/login")
def index():
    usuarios = User.query.all()
    return jsonify(usuarios)


@login.route("/auth/register", methods=["POST"])
def registro():
    user = request.get_json()
    userExists = User.query.filter_by(email=user["email"]).first()
    if not userExists:
        usuario = User(
            email=user["email"],
            password=user["password"],
            first_name=user["first_name"],
            last_name=user["last_name"],
        )
        try:
            db.session.add(usuario)
            db.session.commit()
            mensaje = "Usuario Creado"
        except exc.SQLAlchemyError as e:
            mensaje = "ERROR " + e
    return jsonify({"message": mensaje})


@login.route("/auth/login", methods=["POST"])
def loginChido():
    try:
        user_data = request.get_json()

        if "email" not in user_data or "password" not in user_data:
            raise ValueError("Datos incompletos")

        search_user = User.query.filter_by(email=user_data["email"]).first()

        if search_user and bcrypt.check_password_hash(search_user.password, user_data["password"]):
            auth_token = search_user.encode_auth_token(user_id=search_user.id)
            response = {
                "status": "success",
                "message": "Login exitoso",
                "auth_token": auth_token,
                "user_id": search_user.id
            }
            return jsonify(response)
        else:
            raise ValueError("Datos incorrectos")

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@login.route("/usuarios", methods=["GET"])
@tokenCheck
def getUsers(usuario):
    print(usuario)
    print(usuario["admin"])
    if usuario["admin"]:
        output = []
        usuarios = User.query.all()
        for usuario in usuarios:
            usuarioData = {}
            usuarioData["id"] = usuario.id
            usuarioData["email"] = usuario.email
            usuarioData["password"] = usuario.password
            usuarioData["registered_on"] = usuario.registered_on
            output.append(usuarioData)
        return jsonify({"usuarios": output})
    else:
        return jsonify({"Error": "No tienes permisos"})
