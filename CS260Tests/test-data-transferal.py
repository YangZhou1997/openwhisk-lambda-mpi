#! /bin/python3

import subprocess
from threading import Thread
from threading import Lock
import os
import json
import random
import time
import string
import json as simplejson
import sys



if __name__ == "__main__":
    dataSize = int(sys.argv[1]) # 1 (MB) - 128 (MB)

    funcname1 = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    funcname2 = ''.join(random.sample(string.ascii_letters + string.digits, 8))

    subprocess.check_output("wsk -i action update -t 300000 -m 512 %s ~/openwhisk/CS260Tests/func-data-transferal.py" % (funcname1), shell=True)
    subprocess.check_output("wsk -i action update -t 300000 -m 512 %s ~/openwhisk/CS260Tests/func-data-transferal.py" % (funcname2), shell=True)

    returned_value1 = subprocess.check_output("wsk -i action invoke /whisk.system/%s -p instanceID %s -p dataSize %d" % (funcname1, "myname0", dataSize), shell=True)
    returned_value2 = subprocess.check_output("wsk -i action invoke /whisk.system/%s -p instanceID %s -p dataSize %d" % (funcname1, "myname1", dataSize), shell=True)

    activationID1 = returned_value1.decode("utf-8").split(' ')[5].rstrip()
    activationID2 = returned_value2.decode("utf-8").split(' ')[5].rstrip()

    print(activationID1, activationID2)


    time.sleep(15)
    try:
        returned_value = subprocess.check_output("wsk -i activation get %s | sed '1d'" % (activationID2), shell=True)
        results = json.loads(returned_value.decode("utf-8"))
        comm_time = float(results['response']['result']['res'])
        print(comm_time)
    except subprocess.CalledProcessError as e:
        print(e.output)
