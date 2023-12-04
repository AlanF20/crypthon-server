from flask import Blueprint, request, jsonify
from app import db
from models import User

user_profile = Blueprint("user_profile", __name__)


@user_profile.route("/user_profile/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)

    user_info = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "registered_on": user.registered_on,
        "wallet": [wallet.serialize() for wallet in user.wallet],
        "money_balance": user.money_balance,
        "admin": user.admin,
    }

    return jsonify(user_info)


@user_profile.route("/edit_user/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    user_to_edit = User.query.get(user_id)

    if not user_to_edit:
        return jsonify({"error": "Usuario no encontrado"}), 404
    data = request.get_json()

    if "first_name" in data:
        user_to_edit.first_name = data["first_name"]
    if "last_name" in data:
        user_to_edit.last_name = data["last_name"]
    if "email" in data:
        user_to_edit.email = data["email"]

    db.session.commit()

    return jsonify({"message": "Usuario actualizado correctamente"}), 200


@user_profile.route("/deposit_money_balance/<int:user_id>", methods=["PUT"])
def deposit_money_balance(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if "money_balance" in data:
            new_money_balance = float(data["money_balance"])
            user.money_balance = user.money_balance + new_money_balance

            db.session.commit()

            return jsonify({"message": "Money balance actualizado correctamente"})
        else:
            return (
                jsonify(
                    {
                        "error": "Propiedad 'money_balance' no encontrada en los datos proporcionados"
                    }
                ),
                400,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_profile.route("/withdraw_money_balance/<int:user_id>", methods=["PUT"])
def withdraw_money_balance(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if "money_balance" in data:
            new_money_balance = float(data["money_balance"])
            user.money_balance = user.money_balance - new_money_balance
            db.session.commit()

            return jsonify({"message": "Money balance actualizado correctamente"})
        else:
            return (
                jsonify(
                    {
                        "error": "Propiedad 'money_balance' no encontrada en los datos proporcionados"
                    }
                ),
                400,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
