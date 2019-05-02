#!/bin/bash

docker container stop registry && docker container rm -v registry

docker run -d --restart=always --name registry -v /users/yangzhou/certs:/certs -e REGISTRY_HTTP_ADDR=0.0.0.0:444 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key -p 444:444 registry:2

# Building
cd ..
./gradlew distDocker -PdockerRegistry=node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us:444
cd ansible

[ -f "environments/jenkins/ansible_jenkins.cfg" ] && cp environments/jenkins/ansible_jenkins.cfg ansible.cfg

cd environments/jenkins/
cp node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us.j2.ini hosts.j2.ini
cd group_vars/
cp node-0.mesh-five-nodes.lambda-mpi-pg0.wisc.cloudlab.us all
cd ../../../


#cd /users/yangzhou/incubator-openwhisk-cli
#./gradlew releaseBinaries -Pnativebuild
#cd /users/yangzhou/openwhisk/ansible
#ansible-playbook -i environments/jenkins edge.yml -e mode=clean
#ansible-playbook -i environments/jenkins edge.yml -e cli_installation_mode=local -e openwhisk_cli_home=/users/yangzhou/incubator-openwhisk-cli
#cp /users/yangzhou/incubator-openwhisk-cli/build/wsk /users/yangzhou/openwhisk/bin/

sudo chown -R yangzhou:lambda-mpi-PG0 tmp/
sudo chown -R yangzhou:lambda-mpi-PG0 ../bin/wsk

# for generating db_local.ini; only once needed; you need to change db_host
#ansible-playbook -i environments/jenkins setup.yml
# checking; only once needed.
#ansible-playbook -i environment/jenkins prereq.yml

ansible-playbook -i environments/jenkins openwhisk.yml -e mode=clean
ansible-playbook -i environments/jenkins apigateway.yml -e mode=clean
ansible-playbook -i environments/jenkins couchdb.yml -e mode=clean
ansible-playbook -i environments/jenkins couchdb.yml
ansible-playbook -i environments/jenkins initdb.yml
ansible-playbook -i environments/jenkins wipe.yml
ansible-playbook -i environments/jenkins apigateway.yml
ansible-playbook -i environments/jenkins openwhisk.yml
ansible-playbook -i environments/jenkins properties.yml
ansible-playbook -i environments/jenkins routemgmt.yml
ansible-playbook -i environments/jenkins postdeploy.yml

source ~/.bashrc
# set wsk
wsk property set --apihost 10.10.1.2
wsk property set --auth `cat ~/openwhisk/ansible/files/auth.whisk.system`

wsk sdk install bashauto
source ./wsk_cli_bash_completion.sh
