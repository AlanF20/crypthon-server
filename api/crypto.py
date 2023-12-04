from flask import Blueprint, request, jsonify, Response, send_file
from sqlalchemy import exc
from models import CryptoCurrency, CryptoForm, User, Wallet, Transaction
from app import db, bcrypt
from auth import tokenCheck
import base64
import csv
from io import StringIO

crypto = Blueprint("crypto", __name__)


def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image


def save_image(file):
    image_data = base64.b64encode(file.read()).decode("utf-8")
    return image_data


def load_crypto_data_from_csv(csv_file):
    crypto_data = []
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            crypto_data.append(
                {
                    "cryptoImg": row["cryptoImg"],
                    "cryptoName": row["cryptoName"],
                    "cryptoPrice": row["cryptoPrice"],
                    "cryptoSymbol": row["cryptoSymbol"],
                    "coinIncrement": row["coinIncrement"],
                }
            )
    return crypto_data


@crypto.route("/crypto")
def hello_crypto():
    return jsonify({"message": "entraste a crypthon"})


@crypto.route("/add_crypto", methods=["GET", "POST"])
@tokenCheck
def add_crypto(usuario):
    form = CryptoForm()
    response = {}
    if request.method == "POST":
        crypto_img_encoded = form.encode_image()

        new_crypto = CryptoCurrency(
            cryptoImg=crypto_img_encoded,
            cryptoName=form.cryptoName.data,
            cryptoPrice=form.cryptoPrice.data,
            cryptoSymbol=form.cryptoSymbol.data,
            coinIncrement=form.coinIncrement.data,
        )
        db.session.add(new_crypto)
        db.session.commit()
        response = {"message": f"Se agregó la criptomoneda: {form.cryptoName.data}"}
    else:
        response = {"message": "Hubo un error al añadir la criptomoneda."}
    return jsonify(response)


@crypto.route("/cryptocurrencies", methods=["GET"])
@tokenCheck
def get_all_cryptocurrencies(usuario):
    cryptocurrencies = CryptoCurrency.query.all()

    serialized_cryptos = [crypto.serialize() for crypto in cryptocurrencies]

    return jsonify(serialized_cryptos)


@crypto.route("/edit_crypto/<int:crypto_id>", methods=["PUT"])
@tokenCheck
def edit_crypto(usuario, crypto_id):
    crypto = CryptoCurrency.query.get_or_404(crypto_id)

    if request.method == "PUT":
        crypto.cryptoName = request.form.get("cryptoName", crypto.cryptoName)
        crypto.cryptoPrice = request.form.get("cryptoPrice", crypto.cryptoPrice)
        crypto.cryptoSymbol = request.form.get("cryptoSymbol", crypto.cryptoSymbol)
        crypto.coinIncrement = request.form.get("coinIncrement", crypto.coinIncrement)

        new_image = request.files.get("cryptoImg")
        if new_image:
            crypto.cryptoImg = save_image(new_image)

        db.session.commit()
        return jsonify({"message": "Criptomoneda actualizada correctamente"})
    else:
        return (
            jsonify({"error": "Solicitud no válida. Debe ser 'multipart/form-data'"}),
            400,
        )


@crypto.route("/delete_crypto/<int:crypto_id>", methods=["DELETE"])
@tokenCheck
def delete_crypto(usuario, crypto_id):
    crypto = CryptoCurrency.query.get_or_404(crypto_id)

    db.session.delete(crypto)
    db.session.commit()
    return jsonify({"message": "Criptomoneda eliminada correctamente."})


@crypto.route("/add_crypto_csv", methods=["POST"])
def add_crypto_csv():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No se encontró el archivo CSV"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Nombre de archivo CSV no válido"}), 400

        if file and file.filename.endswith(".csv"):
            crypto_data = load_crypto_data_from_csv(file)
            for crypto_info in crypto_data:
                crypto_img_encoded = convert_image_to_base64(crypto_info["cryptoImg"])
                new_crypto = CryptoCurrency(
                    cryptoImg="sin asignar"
                    if not crypto_img_encoded
                    else crypto_img_encoded,
                    cryptoName=crypto_info["cryptoName"],
                    cryptoPrice=crypto_info["cryptoPrice"],
                    cryptoSymbol=crypto_info["cryptoSymbol"],
                    coinIncrement=crypto_info["coinIncrement"],
                )
                db.session.add(new_crypto)

            db.session.commit()
            return jsonify({"message": "Criptomonedas agregadas correctamente"})
        else:
            return (
                jsonify(
                    {
                        "error": "Formato de archivo no válido. Se requiere un archivo CSV"
                    }
                ),
                400,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crypto.route("/export_crypto_csv", methods=["GET"])
def export_crypto_csv():
    try:
        cryptocurrencies = CryptoCurrency.query.all()

        if not cryptocurrencies:
            return jsonify({"message": "No hay criptomonedas para exportar"}), 404

        crypto_data = []
        for crypto in cryptocurrencies:
            crypto_data.append(
                {
                    "cryptoImg": crypto.cryptoImg,
                    "cryptoName": crypto.cryptoName,
                    "cryptoPrice": crypto.cryptoPrice,
                    "cryptoSymbol": crypto.cryptoSymbol,
                    "coinIncrement": crypto.coinIncrement,
                }
            )

        csv_filename = "cryptocurrencies_export.csv"

        csv_response = Response(
            csv_data(crypto_data),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={csv_filename}"},
        )

        return csv_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def csv_data(data):
    csv_stream = StringIO()
    csv_writer = csv.DictWriter(csv_stream, fieldnames=data[0].keys())

    csv_writer.writeheader()

    csv_writer.writerows(data)

    return csv_stream.getvalue()


@crypto.route("/buy_crypto", methods=["POST"])
def buy_crypto():
    data = request.get_json()
    user_id = data.get("user_id")
    crypto_id = data.get("crypto_id")
    quantity = data.get("quantity")

    user = User.query.get_or_404(user_id)
    crypto = CryptoCurrency.query.get_or_404(crypto_id)

    if not user or not crypto:
        return jsonify({"error": "Usuario o criptomoneda no encontrados"}), 404

    total_cost = float(crypto.cryptoPrice) * quantity
    if total_cost > user.money_balance:
        return jsonify({"error": "Fondos insuficientes"}), 400

    user.money_balance -= total_cost

    wallet_entry = Wallet.query.filter_by(user_id=user_id, crypto_id=crypto_id).first()

    if wallet_entry:
        wallet_entry.quantity += quantity
    else:
        wallet_entry = Wallet(user_id=user_id, crypto_id=crypto_id, quantity=quantity)
        db.session.add(wallet_entry)

    transaction = Transaction(user_id=user_id, crypto_id=crypto_id, amount=quantity)
    db.session.add(transaction)

    db.session.commit()

    return jsonify({"message": "Compra realizada con éxito"})


@crypto.route("/export_transactions", methods=["GET"])
def export_transactions_csv():
    try:
        transactions = Transaction.query.all()

        if not transactions:
            return jsonify({"message": "No hay transacciones para exportar"}), 404

        transaction_data = []
        for transaction in transactions:
            transaction_data.append(
                {
                    "Transaction ID": transaction.id,
                    "User ID": transaction.user_id,
                    "Crypto ID": transaction.crypto_id,
                    "Amount": transaction.amount,
                    "Timestamp": transaction.timestamp.isoformat(),
                }
            )

        csv_filename = "transactions_export.csv"

        csv_response = Response(
            csv_data(transaction_data),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={csv_filename}"},
        )

        return csv_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crypto.route("/wallet/<int:user_id>", methods=["GET"])
@tokenCheck
def get_wallet(usuario, user_id):
    try:
        wallets = Wallet.query.filter_by(user_id=user_id).all()

        if not wallets:
            return jsonify({"message": "Wallet no encontrada"}), 404

        wallet_data = []
        for wallet in wallets:
            data = {
                "walletId": wallet.id,
                "userId": wallet.user_id,
                "cryptoId": wallet.crypto_id,
                "quantity": wallet.quantity,
            }
            crypto = CryptoCurrency.query.get(wallet.crypto_id)
            if crypto:
                data["cryptoData"] = {
                    "cryptoName": crypto.cryptoName,
                    "cryptoPrice": crypto.cryptoPrice,
                    "cryptoSymbol": crypto.cryptoSymbol,
                    "coinIncrement": crypto.coinIncrement,
                    "cryptoImg": crypto.cryptoImg,
                }
            wallet_data.append(data)

        return jsonify(wallet_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
