#!/bin/bash

targeAddr=/etc/docker/certs.d/node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us:444

sudo mkdir -p $targeAddr

sudo cp ./domain.* $targeAddr

sudo cp $targeAddr/domain.crt $targeAddr/domain.cert

echo $targeAddr
sudo ls $targeAddr


