# INSTRUCTIONS

In order to use this code, the following dependencies have to be satisfied.
- install python>=3.6
- install all the dependencies included in requirements.txt

In order to successfully call the ckan API, the user must add its credentials in `.env` file:
- OAUTH_USER: the username of the geodata repository
- OAUTH_PWD: the password of the geodatarepository
To test the download of the files from the geodata repository you need also the access to the messaging system (to get the upload notifications)
- RMQ_USERNAME: the username of the messaging bus system 
- RMQ_PASSWORD: the password of the messaging bus system
- DOWNLOAD_PATH: where to store the file downloaded from the geodata repository

## Upload resources on the geodata repository

In this example we are going to upload a mocked datasets.
All the datasets are stored in `./test_data/datasets/NameDataset`.
They comprehend PDF and delineation maps (Shapefile), but they could also have different formats (txt, JSON, xlsx, docx, etc). 
The metadata instead is stored in `./test_data/metadataINSPIRE_NameDataset.json`. The metadata follow the [INSPIRE metadata guidelines](https://inspire.ec.europa.eu/documents/inspire-metadata-implementing-rules-technical-guidelines-based-en-iso-19115-and-en-iso-1).

The specific metadata for each dataset (datetime start/end, datatype_id) is stored in `.\datasets\NameDataset_resource_metadata`. For each dataset there is a .json file with the same name to describe the resource metadata.
The general metadata we are going to use (`./metadataINSPIRE_NameDataset.json`) contains a JSON dictionary with all the fields compliant to the INSPIRE guidelines. Every value (even the numerical ones) is written as string except the field "spatial" which contains geoJSON geometry.
Any of the dataset linked to a metadata has additional metadata such as temporal validity of the specific file. For example, the metadata can express the temporal validity of the entire block of datasets but a single dataset can have a particular temporal validity.

The upload process of the files occurs in two step:
- upload of the metadata
- iteritative upload of the datasets attaching the reference to the metadata uploaded in the previous step

The file `./upload_data.py` include the code needed to process the data. To run the code: 

`python upload_data.py`

### USEFUL LINKS:
- [INSPIRE metadata guidelines](https://inspire.ec.europa.eu/documents/inspire-metadata-implementing-rules-technical-guidelines-based-en-iso-19115-and-en-iso-1)
- [Validate your geoJSON geometry](geojson.io)
- [CKAN API](http://docs.ckan.org/en/2.10/api/index.html)
- [Table example metadata](./docs/INSPIRE_links.xlsx)


## Download resources from the geodata repository

When a new resource is uploaded on the geodata repository, an automatic notification is sent to the messaging bus.
In the example:
- we simulate the sending of a notification to the bus
- we listen to the bus waiting for the notification
- we use the information contained to retreive and save the resource in local.

The file `./download_data.py` include the code needed to process the data. To run the code: 

`python download_data.py`

NOTE: press ctlr-C to stop the script, otherwise it keeps listening to new messages on the bus
