#!/bin/bash
git pull
docker-compose build && docker-compose up -d
docker logs lmgtfy_app_1 --follow
