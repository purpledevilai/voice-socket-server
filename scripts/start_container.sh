#!/bin/bash


# Docker run
docker run -p 8765:8765 \
  --env-file .env \
  -e PYTHONUNBUFFERED=1 \
  --name voice-socket-server-container \
  -v $(pwd)/src:/app \
  voice-socket-server-image