# !/bin/bash

wsk action -i update test-data-transferal-xfadfxfk /users/yangzhou/openwhisk/CS260Tests/test-data-transferal.py
wsk action -i update test-data-transferal-ksafksdm /users/yangzhou/openwhisk/CS260Tests/test-data-transferal.py

# You might use string as instanceID instead of number
# some parsing error in scala that I have not fixed ...
wsk action -i invoke /whisk.system/test-data-transferal-xfadfxfk -p instanceID myname0 -p dataSize 10000
wsk action -i invoke /whisk.system/test-data-transferal-ksafksdm -p instanceID myname1 -p dataSize 10000