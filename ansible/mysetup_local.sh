#!/bin/bash

# Select a data store
ansible-playbook setup.yml
ansible-playbook prereq.yml

# Building
cd ..
./gradlew distDocker
cd ansible

[ -f "environments/local/ansible_local.cfg" ] && cp environments/local/ansible_local.cfg ansible.cfg


sudo chown -R $USER:lambda-mpi-PG0 tmp/
sudo chown -R $USER:lambda-mpi-PG0 ../bin/wsk


ansible-playbook couchdb.yml
ansible-playbook initdb.yml
ansible-playbook wipe.yml
ansible-playbook openwhisk.yml

# installs a catalog of public packages and actions
ansible-playbook postdeploy.yml

# to use the API gateway
ansible-playbook apigateway.yml
ansible-playbook routemgmt.yml


# set wsk
wsk property set --apihost 10.10.1.2
wsk property set --auth `cat ~/openwhisk/ansible/files/auth.whisk.system`

wsk sdk install bashauto
source ./wsk_cli_bash_completion.sh
