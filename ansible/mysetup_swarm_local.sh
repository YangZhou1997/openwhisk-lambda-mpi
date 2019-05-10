#!/bin/bash

docker swarm init --advertise-addr 10.10.1.1
docker network create --driver=overlay --attachable openwhiskOverlay
