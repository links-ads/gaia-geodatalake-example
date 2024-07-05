import json
import os
from datetime import datetime

import requests

import tools
from config import RabbitMQConfig

ACCESS_TOKEN = None


def callback(channel, method, properties, body):
    """
    Callback function to download the resource
    """
    print(f"[{datetime.now()}] Received {method.routing_key}:{body}")
    try:
        data = json.loads(body)
    except json.decoder.JSONDecodeError as e:
        print(
            "The message on the bus is not a json, someone else is sending example notification not properly formatted"
        )
        return
    resource_id = data.get("id")
    download_resource(resource_id)


def download_resource(resource_id, download_path="./downloaded_data"):
    """
    This function downloads the resource with id = resource_id
    """
    if not resource_id:
        print('The message does not cointain the field "id"')
        return

    # Get the token to access to the geodata repository
    ACCESS_TOKEN = tools.get_access_token()

    # Use the geodata repository API to get the resource information
    url = f'{os.getenv("CKAN_URL")}/api/action/resource_show?id={resource_id}'
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Error:")
            print(response.json())
            raise Exception
    except Exception as e:
        print("Error occurred: " + str(e))

    data = response.json().get("result")
    if not data:
        print("Resource not found")
        return

    # Among the resource information there is the url to download the resource
    # Get the url from the response of the previous API
    url_resource = data.get("url")
    name_resource = os.path.basename(url_resource)

    if not os.path.exists(download_path):
        os.makedirs(download_path)
    filepath = os.path.join(download_path, name_resource)

    # Download the resource. Even this request must be authorized,
    # then add the authorization header
    try:
        response = requests.get(url_resource, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            print("Error:")
            print(response.json())
            raise Exception
    except Exception as e:
        print("Error occurred: " + str(e))

    with open(filepath, "wb") as f:
        f.write(response.content)
    print("Resource saved!")

    return


########################################################################################

# 1 . Mock a notification on the rabbit messaging bus
# NOTE: You don't need to replicate this step since this type of notification is
# automatically sent by the geodata repository when a new data is uploaded

example_notification = "test_data/example_notification.json"
with open(example_notification, "r") as f:
    data = f.read()
    message = json.loads(data)
    tools.send_notification_example(message)

# 2 . Connect to rabbit queue and wait for new messages

conn = tools.connect_to_bus(RabbitMQConfig())
channel = conn.channel()

print("Waiting for messages, press CTRL+C to exit.")
try:
    # start listening and consuming messages
    # callback is the callable function that is triggered when a message is consumed
    channel.basic_consume(
        queue=RabbitMQConfig.queue, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

except KeyboardInterrupt:
    channel.stop_consuming()

finally:
    conn.close()
