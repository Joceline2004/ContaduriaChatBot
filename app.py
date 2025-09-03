from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import re
import unicodedata

app = Flask(__name__)

# Configura tu API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "TU_API_KEY_AQUI")

# Diccionario para guardar historial de conversaciones por usuario
conversations = {}

# Prompt inicial para definir cómo debe comportarse el asistente
system_prompt = """
Eres un asistente virtual académico de la Coordinación de Contaduría.
Debes brindar información clara, breve y profesional.
Responde siempre en español, con tono formal pero amable.
Usa emojis de manera moderada para dar calidez sin perder formalidad.
"""

# --- Utilidad: limpiar texto ---
def limpiar_texto(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9ñáéíóúü\s]", "", texto)
    return texto

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    user_number = request.values.get('From')
    incoming_msg = request.values.get('Body', '').strip()

    resp = MessagingResponse()
    msg = resp.message()

    # Normalizamos el mensaje
    clean_msg = limpiar_texto(incoming_msg)

    # Inicializamos conversación si es la primera vez
    if user_number not in conversations:
        conversations[user_number] = [{"role": "system", "content": system_prompt}]

    # --- Menú inicial ---
    if clean_msg in ["", "hola", "menu", "inicio"]:
        menu_text = (
            "👋 ¡Hola! Soy el asistente virtual de la Coordinación de Contaduría 📚\n\n"
            "Por favor selecciona una opción:\n"
            "1️⃣ Información general\n"
            "2️⃣ Horarios de atención\n"
            "3️⃣ Contacto con la coordinación\n"
            "4️⃣ Pregunta libre (IA)"
        )
        msg.body(menu_text)
        return str(resp)

    # --- Preguntas frecuentes detectadas sin GPT ---
    if any(p in clean_msg for p in ["horario", "hora", "atencion", "abren", "cierran"]):
        msg.body("🕒 El horario de atención es de **9:00 a.m. a 1:00 p.m.**, de lunes a viernes, en los edificios de coordinacion")
        return str(resp)

    if any(p in clean_msg for p in ["contacto", "humano", "asesor", "ayuda", "coordinacion"]):
        msg.body("📞 Puedes comunicarte directamente con la Coordinación de Contaduría al **+52 322 181 6564**.")
        return str(resp)

    if any(p in clean_msg for p in ["informacion", "tramite", "documento", "proceso"]):
        msg.body("📚 Para trámites académicos y administrativos, puedes consultar la página oficial o escribirme tu duda para orientarte.")
        return str(resp)

    if clean_msg in ["1", "2", "3", "4"]:
        if clean_msg == "1":
            msg.body("📚 La Coordinación de Contaduría brinda apoyo en trámites escolares, orientación académica y servicios estudiantiles.")
        elif clean_msg == "2":
            msg.body("🕒 Nuestro horario de atención es de lunes a viernes de 9:00 a.m. a 1:00 p.m.")
        elif clean_msg == "3":
            msg.body("📞 Puedes comunicarte directamente al **+52 322 181 6564** para hablar con la coordinación.")
        elif clean_msg == "4":
            msg.body("✍️ Perfecto, por favor escribe tu consulta y te responderé con IA.")
        return str(resp)

    # --- Si no coincide con nada, enviamos a GPT ---
    try:
        conversations[user_number].append({"role": "user", "content": incoming_msg})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversations[user_number],
            max_tokens=200,
            temperature=0.6
        )

        reply_text = response.choices[0].message["content"].strip()

        conversations[user_number].append({"role": "assistant", "content": reply_text})

    except Exception:
        reply_text = "⚠️ Lo siento, tuve un problema al procesar tu mensaje."

    msg.body(reply_text)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
