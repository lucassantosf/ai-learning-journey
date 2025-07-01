from app import Agent
from flask import Flask, request, jsonify
from utils.logger import agent_logger

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def simple_request():
    # Track request metrics
    agent_logger.track_request(request.method, '/')

    if request.method == 'GET':
        return jsonify({"message": "Hello, this is a simple GET request handler!"})
    
    if request.method == 'POST':
        try:
            agent = Agent()
            data = request.json
            user_question = data.get("prompt")
            
            # Call the agent and log the interaction
            agent_response = agent.call(user_question)
            
            # Log the agent interaction
            agent_logger.log_agent_interaction(
                user_question, 
                agent_response, 
                tools_used=agent.used_tools if hasattr(agent, 'used_tools') else []
            )
            
            return jsonify({"agent": agent_response, "status": "success"})
        
        except Exception as e:
            # Log any errors that occur
            agent_logger.log_error(
                error_type='agent_request_error', 
                error_message=str(e),
                context={
                    'request_data': data,
                    'method': request.method
                }
            )
            return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    agent_logger.start_prometheus_server()
    
    # Run the Flask app
    app.run(debug=True, port=5000)
