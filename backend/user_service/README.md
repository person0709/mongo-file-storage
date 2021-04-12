# User Service for File Storage
____
## Introduction
This server is one of the microservices for File Storage.  
It is responsible for user CRUD operation and authentication/authorization.  
It issues a JWT token that is used for authorization in all the closed endpoints.

## Requirements
* Docker
* Docker-compose
* Python > 3.7

## Endpoints
The list of all the available endpoints.  
For detailed specification, start the server referring to [here](#running-the-server) and open the API documentation page.
### Create User
* Create an account  
  `POST` /api/users  
  `username=[string]`  
  `email=[string]`  
  `password=[string]`
### Get My Info
* Get current user's info  
  `GET` /api/users/my
### Get User List
* Get a list of users by a number of filters 
  `GET` /api/users/  
  `user_id=[string]`  
  `username=[string]`  
  `email=[string]`  
  `role=[string]`  
  `sort_by=[string]`  
  `desc=[bool]`  
  `offset=[int]`  
  `limit=[int]`
### Update User
* Update a user  
  `PUT` /api/users  
  `user_id=[string]`  
  `role=[string]`  
  `storage_allowance=[int]`  
  `is_active=[bool]`
### Delete User  
* Delete a user  
  `DELETE` /api/users  
  `user_id=[string]`
### Issue Token
* Issue a JWT if authenticated  
  `POST` /api/auth/token  
  `username=[string]`  
  `password=[string]`

## How to use
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
A detailed interactive API documentation page is available on <http://localhost:8000/api/users/docs>.

### Superuser
When the server starts up for the first time, the first user is added as an admin which can be used to access any endpoint.  
The credential can be changed by setting environment variables in `.env` file.

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