#!/bin/bash

ssh yangzhou@node-1.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us cat openwhisk/addrMap/test.txt
echo ""
ssh yangzhou@node-2.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us cat openwhisk/addrMap/test.txt
echo ""
ssh yangzhou@node-3.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us cat openwhisk/addrMap/test.txt
echo ""
ssh yangzhou@node-4.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us cat openwhisk/addrMap/test.txt
echo ""
