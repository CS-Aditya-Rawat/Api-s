from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

updates = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    updates.append(data)
    print("Received webhook data:", data)
    socketio.emit('update', data) 
    return jsonify({"status": "success", "data": data}), 200

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
