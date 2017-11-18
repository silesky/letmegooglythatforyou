#!/bin/sh
IMG=sethsil/lmgtfy
PORT_HOST=8000
PORT_CONTAINER=8000

echo "expect host to be: http://0.0.0.0:$PORT_HOST..."
docker run -d -v $(pwd)/img:/img -p $PORT_HOST:$PORT_CONTAINER $IMG
