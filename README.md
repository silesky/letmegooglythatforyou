# README


## Server
```
- install python3.6
- virtualenv -python3.6 venv
- python3.6 -m venv venv
- pip install -r requirements.txt
- . venv/bin/activate
- Run:
  - cd server && python3 app.py
  - or ./immortal.sh
```
## Develop
```
- create a self-signed cert via sh bootstrap.sh
- create .env file:


- debugging redirect does not work over https (with ngrok), so...
  - set SSL_ENABLED to false
  - ngrok http 0.0.0.0:8000
  - save http url and add it to redirect urls: https://api.slack.com/apps/A8477NR70/oauth?
  - go to 0.0.0.0/auth and log in.
```

## DB
```
- docker exec -itu root lmgtfy_db_1 bash
- psql lmgtfy -U postgres
  - list all the tables:
    - SELECT * from teams
- you can access from the app:
  - docker exec -itu root lmgtfy_app_1 bash
  - curl 192.168.99.100:5432 (should show that the port is open)

```
## DB - connect with PGADMIN
```
  - docker-compose up
  - download pgadmin
  - use 192.168.99.100 to connect (and username 'postgres')
  # Create lmgtfy table with PGADMIN
  - then I can use the command line:
  - psql lmgtfy -h docker.local -p 5432 -U postgres

```
### Set up OAuth
```
- get client id and client secret from slack api
- set up redirect url:
  - https://api.slack.com/apps/A8477NR70/oauth?
  - e.g. timeshark.org:8000/redirect or ngrok.../redirect
  - save in 'Oauth and permissions'
- copy an 'add-to-slack' button as static/add_to_slack.html
- when /add-to-slack.html is accessed, it should send this html file
  - app.static('/', './static')
- create a / route for a user who wants to log in
- create an redirect route for after the user logs in - to verify
- read html file as string, and send it (via the html method) whenever a user accesses /auth
- make sure to now click the 'distribute' slack app option -- otherwise the button will not work.
-
```

### Linux
```
- sudo -H pip install pip3
- virtualenv  --python=python3.6 venv
- sudo apt-get install python3.6-venv
- sudo apt-get install python3.6-dev
- python3.6 -m venv venv
- pip3 install -r requirements.txt
- sudo apt-get install libpq-devython-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
- install immortal:
  - sudo apt-get install software-properties-common python-software-properties
  - sudo add-apt-repository ppa:nbari/immortal
  - sudo apt-get update
  - sudo apt-get install immortal
```
## Docker
curl docker.local:5432
```
- cd server
- docker build -t "sethsil/lmgtfy" .
- mount the image folder to the host directory directory (/myHostFolder:/myContainerFolder)
- docker run -it -d -p 8000:8000 -v /img:/app/img sethsil/lmgtfy
- Find the container name: docker ps
- ssh in: docker exec -itu root <containername> bash
```
## Docker-compose
- docker-compose up -d
- troubleshooting:
  - make sure amazee-cachalot start is running
  - make sure the host is 0.0.0.0
  - you can access / send post requests to: (0.0.0.0 will not work)
    - docker.local/stats
    - 192.168.99.100:port
  - you can grab assets from the img volume:
    - docker.local:8000/img/index.html
```
```
# SSL
```
- for local development: bootstrap
  - mkdir ssl/dev
- for server development:
  - Copy and overwrite as part of your cron job:
  - cp -frL /etc/letsencrypt/live/timeshark.org/* /var/www/html/lmgtfy/server/ssl/prod
- you can set the ssl path

```
# Environment Variables
- add a `server/.env` file.
```
API_KEY_BING=
API_KEY_VISION=
API_KEY_FACE=
DEV=TRUE
HOST=http://0.0.0.0
DB_HOST=192.168.99.100
IMAGE_SERVER_BASE=https://timeshark.org:8000
PORT=8000
CLIENT_ID=
CLIENT_SECRET=
```
# FAQ
```
- My images aren't showing up?
  - docker exec -itu root lmgtfy_app_1 bash -- should be in the img
- What letsencrypt path are you using?

`/etc/letsencrypt/live/timeshark.org/privkey.pem`
`/etc/letsencrypt/live/timeshark.org/fullchain.pem`
```
