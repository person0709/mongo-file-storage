# File Store
________________
[![codecov](https://codecov.io/gh/person0709/woven-fs/branch/master/graph/badge.svg?token=TAPD71K67G)](https://codecov.io/gh/person0709/woven-fs)
[![CLI Test](https://github.com/person0709/woven-fs/actions/workflows/cli_test.yaml/badge.svg)](https://github.com/person0709/woven-fs/actions/workflows/cli_test.yaml)
## Introduction
File Store is a service where you can upload and download files on demand.  
It consists of two API microservices, User service and File service, built with [FastAPI](https://github.com/tiangolo/fastapi).  
To interact with the service, it includes a CLI built with [Click](https://github.com/pallets/click), and a frontend built with [Vue](https://github.com/vuejs/vue).

## User Service
User service is a REST API server that is responsible for user account interactions and user authentication/authorization.  
It does the standard CRUD operations on the users as one would expect for use-cases like registering a new account and updating an account
It uses OAuth2's password flow for authentication and issues a JWT for authorization in all closed service endpoints.
### Features
* Create user
* Get user info
* Get list of user info by keyword
* Update user
* Delete user
* Authenticate and issue a JWT token

## File Service
File service is responsible for storing user-uploaded files.  
Conceptually, each user will have their own private "bucket" to store their files.  
All the endpoints in File service require authorization with a JWT
### Features
* Upload file
* Download file
* Get file metadata
* Get list of file metadata by name
* Get storage usage
* Delete file

## Requirements
* Docker
* Docker-compose

## How to set up
You can easily set up the entire service locally including the frontend with simple docker-compose commands.  
The included reverse proxy will route all requests under `http://fs-service.localhost` to appropriate services.
* Edit the included `.env` file if you need to. (Should work as is)
* Build the images
```bash
$ docker-compose build
```
* Run containers
```bash
$ docker-compose up
```
You can now access frontend app via http://fs-service.localhost to interact with the service.  
You can also use included CLI to achieve the same minus some admin features.
