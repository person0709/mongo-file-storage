# CLI for File Store
_____
## Introduction
This is a command line interface(CLI) for File Store.  
You can use this tool to interact with File Store API with ease.

## Requirements
* Python >= 3.7

## How to use
Setup Python venv
```bash
$ python -m venv venv
$ source venv/bin/activate
```
Install CLI package
```bash
$ python -m pip install .
```
You can now use CLI using `fs`.
For example, you can interact with the backend server like following;
```bash
$ fs signup  # sign up for an account
$ fs login  # login
$ fs file upload example_file.txt  # upload file
$ fs file list  # list saved files
$ fs file download --dest save_as.txt example_file.txt  # download file
```
You can check out all the available commands with help flag
```bash
$ fs --help
```

## How to test
The test aims to do full E2E testing.  
Make sure the docker-compose local environment is up.
```bash
# from the project root
$ docker-compose up -d
```
Install requirements
```bash
$ python -m pip install -r requirements.txt
```
Run the tests
```bash
$ python -m pytest .
```
