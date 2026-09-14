import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types
from chatbot_config import MODEL_NAME, SYSTEM_PROMPT

load_dotenv()
app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured in the .env file.")

client = genai.Client(api_key=api_key)

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please enter a wildlife study question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=900,
            ),
        )
        answer = (response.text or "").strip()
        if answer.startswith("[OUT_OF_SCOPE]"):
            answer = answer.replace("[OUT_OF_SCOPE]", "", 1).strip()
        return jsonify({"answer": answer})
    except Exception:
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": "I couldn't connect to WildlifeMate AI right now. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)
