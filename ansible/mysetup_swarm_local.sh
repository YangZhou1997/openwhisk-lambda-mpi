#!/bin/bash

docker swarm init --advertise-addr 130.127.133.154
docker network create --driver=overlay --attachable openwhiskOverlay
