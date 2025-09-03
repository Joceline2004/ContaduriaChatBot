from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAAaxAxtdWV4BPcvWeuzICiXL6SDe5pbQhQw8CSaHONznDi5GgJq1qJZBcHwDpujZCWu2fbymXcnKrqNDtFhpP9s4AtzYfBliUrZAIgZBZBMad01UI0JlAhSFHoZCmhyXBKgxOk0RRsw8HvcrGvn6HjVOZAoINDUwZBk3K5JXZAxCjWBSPZANViZBNZCXnjEJIDqwI8d571bftnsepZBlTLSqvXBbZAx0A0ZCcRVCrJzcIlSMWvT1gelkycZD"
PHONE_NUMBER_ID = "814488218406589"

@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = "mi_token_secreto"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("🌐 Verificación recibida:", mode, token, challenge) 

    # CORRECCIÓN 1: Agregar manejo de caso donde falten parámetros
    if not (mode and token and challenge):
        return "Faltan parámetros", 400

    if token == verify_token:
        return challenge, 200
    else:
        return "Error de verificación", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("🔹 Data recibida:", data)  # CORRECCIÓN 2: imprimir JSON completo para debug

    # CORRECCIÓN 3: Manejar caso cuando no existan mensajes
    try:
        messages = data["entry"][0]["changes"][0]["value"]["messages"]
        message = messages[0]
        from_number = message["from"]
        text = message["text"]["body"]

        # CORRECCIÓN 4: imprimir info de envío para debug
        print(f"Enviando mensaje a {from_number}: {text}")

        send_message(from_number, f"Recibí tu mensaje: {text} ✅")
    except KeyError:
        print("No hay mensajes en este POST")  # evita KeyError si llegan otros eventos
    
    return "ok", 200

def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # ✅ CORRECCIÓN 6: asegurar que el número lleve "+"
    if not to.startswith("+"):
        to = f"+{to}"

    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    # CORRECCIÓN 5: imprimir la respuesta de la API para ver errores
    response = requests.post(url, headers=headers, json=body)
    print("🔹 Response WhatsApp API:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
