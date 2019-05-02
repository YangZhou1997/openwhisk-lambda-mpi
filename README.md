<!--# OpenWhisk with Messaging enhanced-->

# Clone rep:
Under `~/` directory: 
```
git clone git@github.com:YangZhou1997/openwhisk-lambda-mpi.git openwhisk
git clone git@github.com:apache/incubator-openwhisk-cli.git
```

# Machine environment setup: 
```
cd openwhisk
./presetup.sh
```

# WSK CLI setup 
```
cd openwhisk/ansible
./mysetup_cli.sh
```

Then you can choose local setup or distributed setup:  

# Local setup 
``` 
cd openwhisk/ansible
./mysetup_local.sh
```

**Note:** mysetup\_local.sh has only been tested in a bare-metal Ubuntu 16.04.1 LTS (GNU/Linux 4.4.0-142-generic x86\_64)

# Distributed setup
I rent five bare-metal servers from [CloudLab](https://www.cloudlab.us/) each with Ubuntu 16.04.6 LTS (GNU/Linux 4.4.0-145-generic x86_64). 
These five servers are connected with each other using 10GB NIC (Dual-port Intel X520). The hardware details are [here](http://docs.cloudlab.us/hardware.html#%28part._cloudlab-wisconsin%29). 
The five-server cluster is configured using [profile.xml](profile.xml)

Here I want to host controller, crouchDB, redis, zookeeper, nginx, and kafka on node-0, and host one invoker on each of the other nodes (ie, node-1~4).
The basic setup processure follows [Jenkins Pipeline](https://cwiki.apache.org/confluence/display/OPENWHISK/How+to+maintain+the+Jenkins+pipeline+for+OpenWhisk) and the [OpenWhisk Jenkinsfile](https://github.com/apache/incubator-openwhisk/blob/master/Jenkinsfile). 

Machine details: 

| label | host name | domain name | (inner) ip address |
| --- | --- | --- | --- |
| node-0 | node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | 10.10.1.2 |
| node-1 | node-1.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | node-1.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | 10.10.1.5 |
| node-2 | node-2.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | node-2.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | 10.10.1.3 |
| node-3 | node-3.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | node-3.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | 10.10.1.1 |
| node-4 | node-4.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | node-4.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us | 10.10.1.4 |

### Setup SSH for ansible
Make sure that each server can ssh to the other four servers vai ssh without password. 

### Setup private docker registry
From [Jenkins Pipeline](https://cwiki.apache.org/confluence/display/OPENWHISK/How+to+maintain+the+Jenkins+pipeline+for+OpenWhisk): 
> Since we only need to download and build the source code of OpenWhisk on one VM, we need to set up a private docker registry service, so that the docker images we build can be access by other two VMs

On node-0:
```
cp -r openwhisk/certs ./
cd certs

\# generating certificate: fill `node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us` when requiring the domain id
./key_gen.sh

\# setup /etc/docker/certs.d/
./set_certs.sh

\# setup docker registry
./run_registry.sh

\# distributing certificate to other nodes:
./cert_dist.sh
```

On each of the other nodes, run: 
```
cd certs
./set_certs.sh
```

### Build and deploy openwhisk
```
cd openwhisk/ansible
./mysetup_dist.sh
```


