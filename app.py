import requests
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
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
        user_prompt = request.form.get("prompt", "").strip()
        backend_context_file = request.files.get("backend_context")
        page_code_file = request.files.get("page_code")

        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        if not backend_context_file or not page_code_file:
            return jsonify({"error": "Both 'backend_context' and 'page_code' files are required."}), 400

        # Read file contents
        backend_context = backend_context_file.read().decode("utf-8")
        page_code = page_code_file.read().decode("utf-8")

        # Construct request payload
        payload = {
            "input": f"User Prompt: {user_prompt}\nBackend Context: {backend_context}\nModify Page Code: {page_code}"
        }

        # Make request to Azure AI Foundry
        response = requests.post(f"{AZURE_ENDPOINT}/chat/completions", headers=HEADERS, json=payload)

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