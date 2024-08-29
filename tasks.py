import os
import requests
from io import BytesIO
from PIL import Image
import psycopg2
from celery.signals import worker_process_init, worker_process_shutdown
from celery import Celery

db_conn = None

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

NEW_DATA_QUERY = "INSERT INTO images (request_id, product_name, input_url, output_url, status) VALUES (%s, %s, %s, %s, %s)"

@celery.task(name="process_images")
def process_images(data):
    if db_conn is None:
        return "No database connection found."
    imgur_upload_url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID {os.environ.get('IMG_CLIENT_ID', 234)}",
    }
    result_data = []
    for row in data[1:]:
        output_links = []


        for link in row[2:]:
            try:
                image_content = BytesIO(requests.get(link).content)
                if image_content is None:
                    print("Unable to Parse the Image")
                    output_links.append("UNABLE TO LOAD IMAGE")
                    continue
                compressed_image = compress_image(image_content)

                response = requests.post(
                    imgur_upload_url, headers=headers, files={"image": compressed_image}
                )
                resp = response.json()
                if response.status_code != 200:
                    print("Error: ",resp)
                    continue
                output_links.append(resp["data"]["link"])
            except Exception as e:
                print("Error in Loading Image: ", e)

        cur = db_conn.cursor()
        product_id = row[1]
        task_id = process_images.request.id
        input_links = ",".join(row[2:])
        cur.execute(NEW_DATA_QUERY, (task_id, product_id, input_links, ",".join(output_links), "SUCCESS"))
        result_data.append([product_id, input_links, ",".join(output_links)])
        db_conn.commit() 
        cur.close()

    webhook_url = os.environ.get("WEBHOOK_URL", "http://127.0.0.1:5001/webhook")
    payload = {
        "task_id": process_images.request.id,
        "result": result_data
    }
    requests.post(webhook_url, json=payload)
    return True

def compress_image(image_content, quality=50):
    image = Image.open(image_content)
    compressed_image = BytesIO()
    image.save(compressed_image, format=image.format, quality=quality)
    compressed_image.seek(0)
    return compressed_image

@worker_process_init.connect
def init_worker(**kwargs):
    global db_conn
    print("Initiliazing database connection for worker.")
    db_conn = psycopg2.connect(
        dbname=os.environ.get("DATABASE","product"), user=os.environ.get("USER", "adi"), password=os.environ.get("PASSWORD", "test"), host="db", port="5432"
    )

@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global db_conn
    if db_conn:
        print('Closing database connectionn for worker.')
        db_conn.close()
