from flask import Flask, request, jsonify
from utils import validate_csv
from tasks import process_images
from tasks import celery

app = Flask(__name__)

@app.route("/health", methods=['GET'])
def health_check():
    return jsonify({"status": "I am all good"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_data = file.read()

    if file_data is None:
        return jsonify({"error": "No CSV File found, Upload with file tag"}), 400

    data, err = validate_csv(file_data)
    task =  process_images.delay(data)
    return jsonify({"request_id": task.id}), 200

@app.route('/status/<request_id>', methods=['GET'])
def check_status(request_id):
    task_result = celery.AsyncResult(request_id)
    result = {
        "task_id":request_id,
        "task_status": task_result.status # it can also be pending in case of not found the request_id in that case we can make a call to postgreql to check the status of the task, but I want to submit this project as soon as possible
    }
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
