from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def simple_request():
    if request.method == 'GET':
        return jsonify({"message": "Hello, this is a simple GET request handler!"})
    
    if request.method == 'POST':
        data = request.json
        return jsonify({"received": data, "status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
