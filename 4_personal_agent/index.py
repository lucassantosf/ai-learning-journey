from app import Agent
from flask import Flask, request, jsonify
from utils.logger import agent_logger
import traceback
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def simple_request():
    # Track request metrics
    agent_logger.track_request(request.method, '/')

    if request.method == 'GET':
        return jsonify({"message": "Hello, this is a simple GET request handler!"})
    
    if request.method == 'POST':
        try:
            # Ensure request data is not None
            data = request.json or {}
            
            # Extract question with MAXIMUM FALLBACK
            user_question = (
                data.get("prompt") or 
                data.get("question") or 
                data.get("text") or 
                data.get("message") or 
                "Pergunta padrão de fallback"
            )
 
            # FORCE AGENT INITIALIZATION
            try:
                agent = Agent()
            except Exception as init_error:
                response = jsonify({
                    "agent": f"Erro crítico de inicialização: {str(init_error)}",
                    "status": "error",
                    "question": user_question
                })
                return response, 500
            
            # FORCE AGENT CALL WITH MAXIMUM ERROR HANDLING
            try:
                agent_response = agent.call(user_question)
            except Exception as call_error:
                agent_response = f"Erro crítico no processamento: {str(call_error)}"
            
            # ENSURE RESPONSE IS NOT EMPTY
            if not agent_response:
                agent_response = "Resposta padrão: Nenhuma informação disponível"
            
            # FORCE RESPONSE WITH MAXIMUM INFORMATION
            response = jsonify({
                "agent": agent_response, 
                "status": "success",
                "question": user_question,
                "tools_used": agent.used_tools if hasattr(agent, 'used_tools') else [],
                "debug_info": {
                    "raw_request": data,
                    "timestamp": str(datetime.now())
                }
            })
            
            return response
        
        except Exception as e:
            response = jsonify({
                "agent": "Erro crítico e inesperado", 
                "status": "error",
                "error_details": str(e)
            })
            
            return response, 500

if __name__ == '__main__':
    # Configure Flask for MAXIMUM VERBOSITY
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Start Prometheus metrics server
    agent_logger.start_prometheus_server()
    
    # Run the Flask app with EXTREME DEBUGGING
    app.run(
        debug=True, 
        port=5000, 
        host='0.0.0.0',  # Listen on all available interfaces
        threaded=True,   # Enable threading
        processes=1,     # Limit to single process for easier debugging
        use_reloader=True  # Enable auto-reload for development
    )
