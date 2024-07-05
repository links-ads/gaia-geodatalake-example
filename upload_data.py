# api-endpoint

import json
import os
import uuid

import requests
from requests import HTTPError

import tools
from config import GeoDataLakeConfig


def delete_metadata(metadata_id, access_token):
    url = f"{GeoDataLakeConfig.CKAN_URL}/api/action/package_delete"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    body = {"id": metadata_id}
    # data = dataset_string.encode('utf-8')
    try:
        response = requests.post(url, json=body, headers=headers)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6
    else:
        print("Metadata deleted")

    if response.status_code == 200:
        response_dict = response.json()
        assert response_dict["success"] is True
    else:
        print("Error in deleting the metadata:")
        print(response.json())
        raise Exception
    return


def upload_metadata(body, access_token):
    url = f"{GeoDataLakeConfig.CKAN_URL}/api/action/package_create"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    body["name"] = str(uuid.uuid4())
    body["spatial"] = str(body["spatial"]).replace("'", '"')
    # data = dataset_string.encode('utf-8')
    try:
        response = requests.post(url, json=body, headers=headers)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6
    else:
        print("Metadata uploaded")

    if response.status_code == 200:
        response_dict = response.json()
        assert response_dict["success"] is True
        created_package = response_dict["result"]
    else:
        print("Error:")
        print(response.json())
        raise Exception
    return created_package["id"]


def upload_resource(metadata_id, filepath, res_metadata_filepath, access_token):
    url = f"{GeoDataLakeConfig.CKAN_URL}/api/action/resource_create"
    print(f"Uploading {filepath}")
    file = open(filepath)
    _, tail = os.path.split(filepath)
    filename, file_extension = os.path.splitext(tail)

    try:
        with open(res_metadata_filepath) as fp:
            resource_body = json.load(fp)
    except FileNotFoundError:
        print(f"Metadata for file not found: {res_metadata_filepath}")

    if "format" not in resource_body:
        resource_body["format"] = file_extension[1:]

    # add other resource metadata derived from the metadata
    resource_body["package_id"] = metadata_id
    resource_body["name"] = filename

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    try:
        with open(filepath, "rb") as file:
            response = requests.post(
                url, data=resource_body, headers=headers, files=[("upload", file)]
            )
            if response.status_code != 200:
                print("Error:")
                print(response.json())
                raise Exception
    except Exception as e:
        print("Error occurred: " + str(e))
    return


########################################################################################

# 1 . set metadata path and resources path
metadata_filepath = "test_data/metadataINSPIRE_NameDataset.json"
resources_path = "test_data/datasets/NameDataset"
resources_metadata_path = "test_data/datasets/NameDataset_resource_metadata"
access_token = tools.get_access_token()

# 2 . Read JSON data into the metadata_body variable
if metadata_filepath:
    with open(metadata_filepath, "r", encoding="UTF-8") as f:
        metadata_body = json.load(f)

# 3 . upload metadata
metadata_id = upload_metadata(metadata_body, access_token)

print(f"metadata_id: {metadata_id}")

# 4 . uploade datasets
try:
    # iterate on files inside resource_filepath and upload them
    for filename in os.listdir(resources_path):
        upload_resource(
            metadata_id,
            os.path.join(resources_path, filename),
            os.path.join(
                resources_metadata_path, f"{os.path.splitext(filename)[0]}.json"
            ),
            access_token,
        )
    print("DONE!")
except Exception as e:
    print(e)
    # if any error occurs in uploading datasets, delete the metadata
    # (otherwise it will be metadata with no data)
    print("One or more dataset upload failed. Removing the metadata...")
    delete_metadata(metadata_id, access_token)

########################################################################################
