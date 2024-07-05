import os

from dotenv import load_dotenv

load_dotenv()


def trygetenv(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        message = f"Missing expected environment variable: {name}"
        raise ValueError(message)


class RabbitMQConfig:
    """
    Simple configuration class loading RMQ settings from the environment.
    Enter your credentials
    """

    host = trygetenv("RMQ_HOSTNAME")
    port = trygetenv("RMQ_PORT")
    vhost = trygetenv("RMQ_VHOST")
    exchange = trygetenv("RMQ_EXCHANGE")
    queue = trygetenv("RMQ_QUEUE")
    ca_file = trygetenv("RMQ_CA_FILE")
    cert_file = trygetenv("RMQ_CERT_FILE")
    key_file = trygetenv("RMQ_KEY_FILE")
    # uncomment following line if you encounter troubles with certification authority validation
    # CA_FILE = "../cacert.pem"


class GeoDataLakeConfig:
    """
    Simple configuration class loading GeoData Lake settings from the environment.
    Enter your credentials
    """

    CKAN_URL = trygetenv("CKAN_URL")


class OAuth2Config:
    """
    Simple configuration class loading OAuth2 settings from the environment.
    Enter your credentials
    """

    OAUTH_URL = trygetenv("OAUTH_URL")
    OAUTH_API_KEY = trygetenv("OAUTH_API_KEY")
    OAUTH_APP_ID = trygetenv("OAUTH_APP_ID")
    OAUTH_USER = trygetenv("OAUTH_USER")
    OAUTH_PWD = trygetenv("OAUTH_PWD")
