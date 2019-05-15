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
        # print(activationID)

        self.fib_id[work_id] = activationID


    def start_fibs(self):
        for i in range(0, self.fib_num):
            self.start_function_instance(i)

        time.sleep(300)

        for i in range(0, self.fib_num):
            try:
                returned_value = subprocess.check_output("wsk -i activation get %s | sed '1d'" % (self.fib_id[i]), shell=True)
            except subprocess.CalledProcessError as e:
                # print(self.fib_id[i])
                # print(e.output)
                continue

            if returned_value == None:
                continue
            try:
                results = json.loads(returned_value.decode("utf-8"))
                self.fib_log[i] = results
                # print(results)
            except json.decoder.JSONDecodeError as e:
                continue


if __name__ == "__main__":
    num_fib = int(sys.argv[1])
    wsk_ts_test = wsk_fib(num_fib, 39)
    wsk_ts_test.create_func()
    wsk_ts_test.start_fibs()

    usertime = 0.0
    systime = 0.0
    inittime = 0.0

    usertimeArray = []
    systimeArray = []
    inittimeArray = []

    error_count = 0
    warm_start = 0

    f = open("annotations.txt", 'w')
    for i in range(0, wsk_ts_test.fib_num):
        simplejson.dump(wsk_ts_test.fib_log[i], f)
        f.write("----------------------------------------------\n")

        if wsk_ts_test.fib_log[i] == None:
            error_count += 1
            # print('activation error for %s' % (wsk_ts_test.fib_id[i]))
        elif 'fibonacci' not in wsk_ts_test.fib_log[i]['response']['result']:
            error_count += 1
            # print('%s for %s' % (wsk_ts_test.fib_log[i]['response']['result'], wsk_ts_test.fib_id[i]))
        else:
            startType = ['warm', 'cold'][len(wsk_ts_test.fib_log[i]['annotations']) == 6]
            # print('fib results: %d; %s' % (wsk_ts_test.fib_log[i]['response']['result']['fibonacci'], startType))

            temp = wsk_ts_test.fib_log[i]['duration']
            usertimeArray.append(temp)
            usertime += temp

            temp = wsk_ts_test.fib_log[i]['annotations'][1]['value']
            systimeArray.append(temp)
            systime += temp

            if startType == 'cold':
                temp = wsk_ts_test.fib_log[i]['annotations'][5]['value']
                inittimeArray.append(temp)
                inittime += temp
                warm_start += 1


    print('average waiting time: %f' % (systime / (wsk_ts_test.fib_num - error_count)))
    print(systimeArray)

    print('average execution time: %f' % (usertime / (wsk_ts_test.fib_num - error_count)))
    print(usertimeArray)

    print('average init time: %f' % (inittime / warm_start))

    print('successful instances number: %s' % (wsk_ts_test.fib_num - error_count))
    f.close()


    # Does not work??
    # for fiblog in wsk_ts_test.fib_log:
    #     print(fiblog['duration'])

