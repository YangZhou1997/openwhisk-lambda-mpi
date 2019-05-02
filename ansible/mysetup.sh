# Select a data store
ansible-playbook setup.yml

# Building
cd ..
./gradlew distDocker
cd ansible

sudo chown -R yangzhou:lambda-mpi-PG0 tmp/
sudo chown -R yangzhou:lambda-mpi-PG0 ../bin/wsk


echo "prereq.yml"
ansible-playbook prereq.yml

echo "couchdb.yml"
ansible-playbook couchdb.yml
echo "initdb.yml"
ansible-playbook initdb.yml
echo "wipe.yml"
ansible-playbook wipe.yml
echo "openwhisk.yml"
ansible-playbook openwhisk.yml

# installs a catalog of public packages and actions
echo "postdeploy.yml"
ansible-playbook postdeploy.yml

# to use the API gateway
echo "apigateway.yml"
ansible-playbook apigateway.yml
echo "routemgmt.yml"
ansible-playbook routemgmt.yml


# set wsk
wsk property set --apihost 10.10.1.2
wsk property set --auth `cat ~/openwhisk/ansible/files/auth.whisk.system`

wsk sdk install bashauto
source ./wsk_cli_bash_completion.sh
