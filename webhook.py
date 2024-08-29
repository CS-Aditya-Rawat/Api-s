from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received webhook data:", data)
    return jsonify({"status": "success", "data": request.json}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

