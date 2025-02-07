import requests
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Azure AI Foundry API Configuration
AZURE_ENDPOINT = os.getenv("ENDPOINT")
AZURE_API_KEY = os.getenv("API_KEY")

if not AZURE_ENDPOINT or not AZURE_API_KEY:
    raise ValueError("Missing AZURE_ENDPOINT or AZURE_API_KEY. Check your .env file.")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AZURE_API_KEY}"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Chatbot API is running"}), 200

@app.route("/chat", methods=["POST"])
def chatbot():
    try:
        data = request.json

        # Validate request data
        if not data or "prompt" not in data or "backend_context" not in data or "page_code" not in data:
            return jsonify({"error": "Invalid request. 'prompt', 'backend_context', and 'page_code' are required."}), 400

        user_prompt = data.get("prompt", "").strip()
        backend_context = data.get("backend_context", "").strip()
        page_code = data.get("page_code", "").strip()

        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Construct request payload
        payload = {
            "input": f"User Prompt: {user_prompt}\nBackend Context: {backend_context}\nModify Page Code: {page_code}"
        }

        # Make request to Azure AI Foundry
        response = requests.post(f"{AZURE_ENDPOINT}/v1/inference", headers=HEADERS, json=payload)

        if response.status_code == 200:
            modified_code = response.json().get("output", "No output generated")
            return jsonify({"modified_code": modified_code}), 200
        else:
            return jsonify({
                "error": "Failed to generate response from Azure API",
                "status_code": response.status_code,
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)