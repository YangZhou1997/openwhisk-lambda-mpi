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

class wsk_fib:
    def __init__(self, fib_num, number):
        self.fib_num = fib_num
        self.finished_fib_num = 0
        self.fib_para = number

        self.lock = Lock()
        self.fib_id = [None] * 3600
        self.fib_log = [None] * 3600

        # self.funcName = ['test_a','test_b','test_c','test_d',
        #                  'test_e','test_f','test_g','test_h',
        #                  'test_i','test_j','test_k','test_l',
        #                  'test_l','test_m','test_n','test_o']

        self.funcName = [''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(16)]


    def create_func(self):
        for i in range(0, len(self.funcName)):
            # subprocess.check_output("wsk -i action update -t 300000 --docker yangzhou1997/python3action:mpi %s ~/openwhisk/functions/test-random/fib.py" % (self.funcName[i]), shell=True)
            subprocess.check_output("wsk -i action update -t 300000 %s ~/openwhisk/functions/test-random/fib.py" % (self.funcName[i]), shell=True)


    def start_function_instance(self, work_id):
        random_func = self.funcName[random.randint(0,len(self.funcName) - 1)]

        returned_value = subprocess.check_output("wsk -i action invoke %s -p number %d -p instanceID %s" % (random_func, self.fib_para, ''.join(random.sample(string.ascii_letters + string.digits, 8))), shell=True)

        # ok: invoked /_/fib with id 046616d8795d43eaa616d8795db3ea95
        activationID = returned_value.decode("utf-8").split(' ')[5].rstrip()
        print(activationID)

        self.fib_id[work_id] = activationID


    def start_fibs(self):
        for i in range(0, self.fib_num):
            self.start_function_instance(i)

        time.sleep(150)

        for i in range(0, self.fib_num):
            returned_value = subprocess.check_output("wsk -i activation get %s | sed '1d'" % (self.fib_id[i]), shell=True)
            results = json.loads(returned_value.decode("utf-8"))
            self.fib_log[i] = results
            # print(results)


if __name__ == "__main__":
    wsk_ts_test = wsk_fib(64, 39)
    wsk_ts_test.create_func()
    wsk_ts_test.start_fibs()
    duration = 0.0
    f = open("annotations.txt", 'w')
    for i in range(0, wsk_ts_test.fib_num):
        simplejson.dump(wsk_ts_test.fib_log[i], f)
        f.write("----------------------------------------------\n")
        print(wsk_ts_test.fib_log[i]['response']['result']['fibonacci'])
        print(len(wsk_ts_test.fib_log[i]['annotations']))
        duration += wsk_ts_test.fib_log[i]['duration']
    print(duration / wsk_ts_test.fib_num)
    f.close()


    # Does not work??
    # for fiblog in wsk_ts_test.fib_log:
    #     print(fiblog['duration'])



