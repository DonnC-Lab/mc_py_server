# MiniCampus Server

## Features
Conect to [*deta]() backend services for some of the MC modules

## Offline, Interactive docs
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Run
Create virtual env

Install requirements with
```bash
$ pip install -r requirements.txt
```

Start server
```bash
$ uvicorn main:app --reload
```

## Auth keys
Register for account on deta

Create a `.env` file in the root directory and create your `project_key` var

Paste your project key you get from your deta dashboard
```
DETA_PROJECT_KEY = <project_key>
```