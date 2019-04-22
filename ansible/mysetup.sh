# Select a data store
ansible-playbook setup.yml

# Building
cd ..
./gradlew distDocker
cd ansible

sudo chown -R yangzhou:lambda-mpi-PG0 tmp/

ansible-playbook prereq.yml

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
wsk property set --apihost 172.17.0.1
wsk property set --auth `cat ~/openwhisk/ansible/files/auth.whisk.system`

wsk sdk install bashauto
source ./wsk_cli_bash_completion.sh
