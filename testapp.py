import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace this with your Colab URL
COLAB_URL = "https://2e04-35-227-24-81.ngrok-free.app/llm"  # Change this to your ngrok URL

# Endpoint to interact with the Colab LLM
@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        # Get the prompt from the request body
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Send the prompt to the Colab LLM endpoint
        response = requests.post(COLAB_URL, json={"prompt": prompt})
        
        # Check if response is valid
        if response.status_code == 200:
            llm_response = response.json()
            return jsonify({"response": llm_response.get('response')})
        else:
            return jsonify({"error": "Failed to get response from Colab LLM"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Test route
@app.route('/')
def home():
    return "Flask is running. Use /get_response to interact with LLM."


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
