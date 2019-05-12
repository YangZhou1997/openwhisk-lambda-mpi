#!/bin/bash

cd ~/incubator-openwhisk-cli
./gradlew releaseBinaries -Pnativebuild
cd ~/openwhisk/ansible

ansible-playbook -i environments/jenkins edge.yml -e mode=clean
ansible-playbook -i environments/jenkins edge.yml -e cli_installation_mode=local -e openwhisk_cli_home=~/incubator-openwhisk-cli

cp ~/incubator-openwhisk-cli/build/wsk ~/openwhisk/bin/
