#!/bin/bash

cd /users/yangzhou/incubator-openwhisk-cli
./gradlew releaseBinaries -Pnativebuild
cd /users/yangzhou/openwhisk/ansible
ansible-playbook -i environments/jenkins edge.yml -e mode=clean
ansible-playbook -i environments/jenkins edge.yml -e cli_installation_mode=local -e openwhisk_cli_home=/users/yangzhou/incubator-openwhisk-cli

cp /users/yangzhou/incubator-openwhisk-cli/build/wsk /users/yangzhou/openwhisk/bin/
