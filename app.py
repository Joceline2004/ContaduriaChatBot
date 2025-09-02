from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAAJfrdqlqq0BPXDafvSNpgdpSTq5Xg1ZBm2IZAkJ0u2TP0H1HKZChgFZBphGkcUPr7fgnK8MsAROhRKO8tpajmSGtmzBKWt5BOmRnZBPvBKZAcKuSZCFfoukZB7ccTC7r6D5h2889O4WB2MZBuhVshDrQNF9TIMlvZCDrnszh5GQLuFj09UXE3WEwREnOWWPTUscwRsbkcflU5iiEHIbbfKJTNz4uZCgSUgZBxMAkyzS0ZAIwgAZDZD"
PHONE_NUMBER_ID = "751332178071615"

@app.route("/webhook", methods=["GET"])
def verify():
    # Verificación con Meta
    verify_token = "mi_token_secreto"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if token == verify_token:
            return challenge, 200
        else:
            return "Error de verificación", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)  # Para debug en consola

    if "messages" in data["entry"][0]["changes"][0]["value"]:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        # Aquí programas la respuesta que quieras
        send_message(from_number, f"Recibí tu mensaje: {text} ✅")
    return "ok", 200

def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=body)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
