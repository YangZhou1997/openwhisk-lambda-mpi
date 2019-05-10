#!/bin/bash

echo "node0: setup swarm service on node1-4"

node1=10.10.1.5
node2=10.10.1.3
node3=10.10.1.1
node4=10.10.1.4

echo "node1 tries to be the swarm manager"
ssh yangzhou@$node1 docker swarm leave --force
TOKEN="$(ssh yangzhou@$node1 docker swarm init --advertise-addr 10.10.1.5 | sed 's/.*--token \(\S*\).*/\1/' | sed -n '5p')"
echo "the token is $TOKEN"

echo "node2 tries to join"
ssh yangzhou@$node2 docker swarm leave
ssh yangzhou@$node2 docker swarm join --token $TOKEN --advertise-addr $node2 $node1:2377

echo "node3 tries to join"
ssh yangzhou@$node3 docker swarm leave
ssh yangzhou@$node3 docker swarm join --token $TOKEN --advertise-addr $node3 $node1:2377

echo "node4 tries to join"
ssh yangzhou@$node4 docker swarm leave
ssh yangzhou@$node4 docker swarm join --token $TOKEN --advertise-addr $node4 $node1:2377

echo "node1 create attachable overlay network"
ssh yangzhou@$node1 docker network create --driver=overlay --subnet 10.0.0.0/8 --attachable openwhiskOverlay
