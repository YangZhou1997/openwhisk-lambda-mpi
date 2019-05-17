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
    # testFunc = "func-data-transferal.py"
    testFunc = sys.argv[2]
    sendNum = int(sys.argv[3])

    dataSize = int(sys.argv[1]) # 1 (MB) - 128 (MB)

    funcname1 = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    funcname2 = ''.join(random.sample(string.ascii_letters + string.digits, 8))

    subprocess.check_output("wsk -i action update --docker yangzhou1997/python3action:mpi -t 300000 -m 512 %s ~/openwhisk/CS260Tests/%s.py" % (funcname1, testFunc), shell=True)
    subprocess.check_output("wsk -i action update --docker yangzhou1997/python3action:mpi -t 300000 -m 512 %s ~/openwhisk/CS260Tests/%s.py" % (funcname2, testFunc), shell=True)

    returned_value1 = subprocess.check_output("wsk -i action invoke /whisk.system/%s -p instanceID %s -p dataSize %d -p sendNum %d" % (funcname1, "myname0", dataSize, sendNum), shell=True)
    returned_value2 = subprocess.check_output("wsk -i action invoke /whisk.system/%s -p instanceID %s -p dataSize %d -p sendNum %d" % (funcname1, "myname1", dataSize, sendNum), shell=True)

    activationID1 = returned_value1.decode("utf-8").split(' ')[5].rstrip()
    activationID2 = returned_value2.decode("utf-8").split(' ')[5].rstrip()

    # print(activationID1, activationID2)

    if testFunc == "func-data-transferal-redis":
        time.sleep(30)
    else:
        time.sleep(10)
    try:
        returned_value = subprocess.check_output("wsk -i activation get %s | sed '1d'" % (activationID2), shell=True)
        results = json.loads(returned_value.decode("utf-8"))
        comm_time = float(results['response']['result']['res'])
        print(comm_time)
    except subprocess.CalledProcessError as e:
        print(e.output)
