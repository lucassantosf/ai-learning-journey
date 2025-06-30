from app import Agent
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def simple_request():
    if request.method == 'GET':
        return jsonify({"message": "Hello, this is a simple GET request handler!"})
    
    if request.method == 'POST':
        agent = Agent()
        data = request.json
        user_question = data.get("prompt")
        agent_response = agent.call(user_question)
        return jsonify({"agent": agent_response, "status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)