#!/bin/bash


# Docker run
docker run -p 9000:9000 \
  --name voice-socket-server-container \
  -it \
  --env-file .env \
  -e PYTHONUNBUFFERED=1 \
  -v $(pwd)/src:/app \
  voice-socket-server-image