#! ../venv/bin/python3

import subprocess
from threading import Thread
from threading import Lock
import os
import json
import random

class wsk_fib:
    def __init__(self, fib_num, number):
        self.fib_num = fib_num
        self.finished_fib_num = 0
        self.fib_para = number

        self.lock = Lock()
        self.fib_id = [None] * 2000
        self.fib_res = [None] * 2000

        self.funcName = ['test_a','test_b','test_c','test_d',
                         'test_e','test_f','test_g','test_h',
                         'test_i','test_j','test_k','test_l',
                         'test_l','test_m','test_n','test_o']

    def create_func(self):
        for i in range(0, len(self.funcName)):
            subprocess.check_output("wsk -i action create --docker yangzhou1997/python3action:mpi %s ~/openwhisk/functions/test-random/fib.py" % (self.funcName[i]), shell=True)


    def start_function_instance(self, work_id):
        random_func = random.randint(0,len(self.funcName) - 1)
        # ok: invoked /_/fib with id 046616d8795d43eaa616d8795db3ea95
        returned_value = subprocess.check_output("wsk -i action invoke %s -p number %d" % (random_func, work_id), shell=True)
        activationID = returned_value.split(" ")[5]
        print activationID

        self.fib_id[work_id] = activationID

            # json.loads(returned_value)

        with self.lock:
            # print "Lock Acquired"
            self.finished_fib_num += 1

    def start_fibs(self):
        for i in range(0, self.mapper_num):
            p = Thread(target=self.start_function_instance, args=(i))
            p.start()
        if self.finished_mapper_num == self.mapper_num:
            return


if __name__ == "__main__":
    wsk_ts_test = wsk_fib(1800, 30)
    wsk_ts_test.start_fibs()
    for i in wsk_ts_test.mapper_res:
        print(i)


