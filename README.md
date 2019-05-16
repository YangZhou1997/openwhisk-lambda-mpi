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
###################only once####################
# Select a data store
ansible-playbook setup.yml
ansible-playbook prereq.yml
# you might need to change in db_local.ini: host to 172.17.0.1
###################only once####################
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
These five servers are connected with each other using 10GB NIC (Dual-port Intel X520). 
The specific hardware type is [c220g2](http://docs.cloudlab.us/hardware.html#%28part._cloudlab-wisconsin%29). 
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

### Overlay network in Swarm Mode
```
cd openwhisk/ansible
./mysetup_swarm.sh
```

### Setup SSH for ansible
Make sure that each server can ssh to the other four servers vai ssh without password. 

### Setup private docker registry
From [Jenkins Pipeline](https://cwiki.apache.org/confluence/display/OPENWHISK/How+to+maintain+the+Jenkins+pipeline+for+OpenWhisk): 
> Since we only need to download and build the source code of OpenWhisk on one VM, we need to set up a private docker registry service, so that the docker images we build can be access by other two VMs

On node-0:
```
cp -r openwhisk/certs ./
cd certs

# generating certificate: fill `node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us` when requiring the domain id
./key_gen.sh

# setup /etc/docker/certs.d/
./set_certs.sh

# setup docker registry
./run_registry.sh

# distributing certificate to other nodes:
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


# Functionality Supported

Users specify function instance ID using ```-p instanceID name0``` during invoking time, 
while our **Directory Service** will let each function instance know the IP addresses and survival status of its peer instances during runtime. 

Note that due to some weird reason in Scala String parsing, we only support using String as instand ID instead of using pure numbers. 

User creats function: 
```
wsk -i action update --docker yangzhou1997/python3action:mpi fib ~/openwhisk/functions/test-random/fib.py
```
User invokes function instances:
```
wsk -i action invoke fib -p number 39 -p instanceID myname0
wsk -i action invoke fib -p number 39 -p instanceID myname1
wsk -i action invoke fib -p number 39 -p instanceID myname2
wsk -i action invoke fib -p number 39 -p instanceID myname3
```

You should be able to see the ```~/openwhisk/addrMap/addrMap.txt``` during function instance runtime as follows: 
```
myname0=10.0.0.184&myname1=10.0.0.185&myname2=10.0.0.129&myname3=10.0.0.112
```

The appearence of ```instanceID=IP``` means that function instance is still alive. 
Note that we have set the default synchronization time interval to 1s. 
Thus, out Directory Service cannot provide any IP whose corresponding container lives for less than 1s. 
