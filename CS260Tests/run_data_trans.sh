# !/bin/bash

wsk action -i update -t 300000 -m 512 func-data-transferal-xfadfxfk /users/yangzhou/openwhisk/CS260Tests/func-data-transferal.py
wsk action -i update -t 300000 -m 512 func-data-transferal-ksafksdm /users/yangzhou/openwhisk/CS260Tests/func-data-transferal.py

# You might use string as instanceID instead of number
# some parsing error in scala that I have not fixed ...
wsk action -i invoke /whisk.system/func-data-transferal-xfadfxfk -p instanceID myname0 -p dataSize 128
wsk action -i invoke /whisk.system/func-data-transferal-ksafksdm -p instanceID myname1 -p dataSize 128