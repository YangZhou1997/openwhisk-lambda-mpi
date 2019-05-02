#!/usr/bin/env bash

sudo apt-get update
sudo apt-get -y install byobu

# bad: something is wrong with python's default openssl
sudo rm -rf /usr/lib/python2.7/dist-packages/OpenSSL
sudo rm -rf /usr/lib/python2.7/dist-packages/pyOpenSSL-0.15.1.egg-info
sudo pip install pyopenssl

cd tools/ubuntu-setup && ./all.sh
sudo usermod -a -G docker $USER

echo "export OPENWHISK_TMP_DIR=/users/yangzhou/openwhisk/ansible/tmp" >> ~/.bashrc
echo "export PATH=/users/yangzhou/openwhisk/bin:$PATH" >> ~/.bashrc

echo "alias wsk-local='WSK_CONFIG_FILE=~/.wskprops-local wsk -i'" >> ~/.bashrc
echo "alias wsk='wsk -i'" >> ~/.bashrc
echo "alias dc='docker'" >> ~/.bashrc
echo "alias ll='ls -lh'" >> ~/.bashrc
echo "alias python='python3'" >> ~/.bashrc
echo "alias pip='pip3'" >> ~/.bashrc

source ~/.bashrc

