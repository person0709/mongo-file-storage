# File Service for File Storage
____
## Introduction
This server is one of the microservices for File Storage.  
It is responsible for file CRUD operations.  
Conceptually, each user will have their own storage space to store their files, which is private from other users (excluding admins).

## Requirements
* Docker
* Docker-compose
* Python > 3.7

## Endpoints
The list of all the available endpoints.  
For detailed specification, start the server referring to [here](#running-the-server) and open the API documentation page.
### Upload File
* Upload a file  
  `POST` /api/files/upload  
  `file=[file in multipart/form-data]`
### Download File
* Download a file  
  `GET` /api/files/download  
  `filename=[string]`
### Get File Metadata
* Get a metadata of a file  
  `GET` /api/files  
  `filename=[string]`
### Get File Metadata List
* Get a list of file metadata  
  `GET` /api/files/list/  
  `sort_by=[string]`  
  `desc=[bool]`  
  `offset=[int]`  
  `limit=[int]`
### Search File  
* Search files by regex  
  `GET` /api/files/search/  
  `pattern=[string]`  
  `limit=[int]`
### Count File
* Count the total number of uploaded files  
  `GET` /api/files/count
### Delete File
* Delete a file  
  `DELETE` /api/files  
  `filename=[string]`

## How to use
### No-auth mode
This service is supposed to be used along-side with User Service microservice for authentication and authorization.   
However, there is a no-auth mode implemented, so it can be used on its own without auth.  
All you need to do is set the environment variable `NO_AUTH_MODE` to `True` in the docker-compose file.
```yaml
    environment:
      MONGODB_URL: mongodb://${MONGO_DB_USERNAME}:${MONGO_DB_PASSWORD}@${MONGO_DB_HOST}:27017
#      NO_AUTH_MODE: "True"  # uncomment to enable no-auth mode
```
### Running the server
Edit the included `.env` file if you want to. (It should run as is)

Build image
```bash
$ docker-compose build
```
Run the server
```bash
$ docker-compose up
```
The server should be up and running on <http://localhost:8000>.  
A detailed interactive API documentation page is available on <http://localhost:8000/api/files/docs>.


## How to test
You can either test locally or in a docker-compose environment.
### Local
(Optional) Setup venv
```bash
$ python -m venv venv
$ source venv/bin/activate
```

Install dependencies
```bash
# this will also install pytest
$ python -m pip install -r requirements.txt
```

Deploy test MongoDB
```bash
$ docker run --rm --name mongodb -d -p 27017:27017 mongo:4.4
```

Run tests
```bash
$ python -m pytest .
```

### Using docker-compose
Build image
```bash
$ docker-compose build
```

Run tests
```bash
$ docker-compose run file-service python -m pytest .
```

Tear down
```bash
$ docker-compose down
```