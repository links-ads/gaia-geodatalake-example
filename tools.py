import json
import os
import ssl

import pika
import requests
from requests import HTTPError

from config import OAuth2Config, RabbitMQConfig

REFRESH_TOKEN = None


# Get access token
def get_access_token():
    global REFRESH_TOKEN
    url = f"{OAuth2Config.OAUTH_URL}/api/login"
    body = {
        "loginId": OAuth2Config.OAUTH_USER,
        "password": OAuth2Config.OAUTH_PWD,
        "applicationId": OAuth2Config.OAUTH_APP_ID,
        "noJWT": False,
    }
    headers = {
        "Authorization": OAuth2Config.OAUTH_API_KEY,
    }
    try:
        response = requests.post(url, json=body, headers=headers)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6
    else:
        print("Access Token obtained")
    if response.status_code == 200:
        REFRESH_TOKEN = response.json()["refreshToken"]
    else:
        print("Error:")
        print(response.json())
        raise Exception
    return response.json()["token"]


def refresh_token():
    url = f"{OAuth2Config.OAUTH_URL}/jwt/refresh"
    body = {"refresh_token": REFRESH_TOKEN}
    try:
        response = requests.post(url, data=body)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6
    else:
        print("Access Token obtained")

    return response.json()["token"]


def connect_to_bus(config):
    ca_file = os.path.abspath(config.ca_file)
    cert_file = os.path.abspath(config.cert_file)
    key_file = os.path.abspath(config.key_file)
    assert os.path.exists(ca_file), f"CA certificate file not found: {ca_file}"
    assert os.path.exists(cert_file), f"Client certificate file not found: {cert_file}"
    assert os.path.exists(key_file), f"Client key file not found: {key_file}"

    credentials = pika.credentials.ExternalCredentials()
    ssl_options = get_tls_parameters(config.host, ca_file, cert_file, key_file)

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=credentials,
                virtual_host=config.vhost,
                host=config.host,
                port=config.port,
                ssl_options=ssl_options,
            )
        )
    except Exception as e:
        print("Error:", str(e))
        raise

    return connection


def get_notification(message):
    config = RabbitMQConfig()
    connection = connect_to_bus(config)
    try:
        channel = connection.channel()

        datatype_id = message.get("datatype_id")
        routing_key = f"geodata.{datatype_id[0]}.{datatype_id[1]}.{datatype_id}"
        # send the message on the given exchange, with the required routing key and body
        channel.basic_publish(
            exchange=config.exchange,
            routing_key=routing_key,
            body=json.dumps(message),
        )

        connection.close()
    except Exception as e:
        print("Error:", str(e))


def send_notification_example(message):
    config = RabbitMQConfig()

    connection = connect_to_bus(config)
    try:
        channel = connection.channel()

        datatype_id = message.get("datatype_id")
        routing_key = f"geodata.{datatype_id[0]}.{datatype_id[1]}.{datatype_id}"
        # send the message on the given exchange, with the required routing key and body
        channel.basic_publish(
            exchange=config.exchange,
            routing_key=routing_key,
            body=json.dumps(message),
        )

        connection.close()
    except Exception as e:
        print("Error:", str(e))


def get_tls_parameters(hostname: str, ca_cert_file: str, cert_file: str, key_file: str):
    context = ssl.create_default_context(cafile=ca_cert_file)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(
        certfile=cert_file,
        keyfile=key_file,
    )
    return pika.SSLOptions(context, server_hostname=hostname)
