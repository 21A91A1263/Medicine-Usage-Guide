from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

# GROQ API Configuration
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! ")

# Function to get medicine details from Groq API
def get_medicine_info(medicine_name):
    prompt = (
        f"Provide structured details about the medicine '{medicine_name}' in JSON format with the following fields: "
        "'name' (medicine name), 'usage' (what it is used for), 'timing' (when to take it - morning/after lunch/before lunch), "
        "'how_to_use' (instructions for use), 'precautions' (safety measures), 'side_effects' (potential issues), "
        "'specialist' (which doctor to consult), and a final note 'warning' with 'Please consult a doctor if any doubts arise.'. "
        "Ensure the output is a valid JSON format and if given '{medicine_name}' is not medicine then send ' medicine not found in' 'usage'."
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(GROQ_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        result = response.json()

        # Extract and validate response
        if "choices" in result and result["choices"]:
            raw_info = result["choices"][0]["message"]["content"]

            # Remove code block formatting if present
            if raw_info.startswith("```json"):
                raw_info = raw_info.strip("```json").strip("```")

            # Convert string to JSON
            return json.loads(raw_info)
        else:
            return {"error": "No valid response received from AI."}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

# Route for Frontend UI
@app.route("/")
def home():
    return render_template("index.html")

# API Endpoint to Get Medicine Information
@app.route("/medicine_info", methods=["POST"])
def medicine_info():
    data = request.get_json()
    if not data or "medicine_name" not in data:
        return jsonify({"error": "Medicine name is required"}), 400

    medicine_name = data["medicine_name"]
    details = get_medicine_info(medicine_name)

    return jsonify({"medicine_name": medicine_name, "details": details})

if __name__ == "__main__":
    app.run(debug=True)
