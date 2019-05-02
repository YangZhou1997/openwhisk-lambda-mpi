#!/bin/bash/python3
import subprocess
from threading import Thread
from threading import Lock
import os
import json

class wsk_terasort:
    def __init__(self, mapper_num, reducer_num):
        self.mapper_num = mapper_num
        self.reducer_num = reducer_num
        self.finished_mapper_num = 0
        self.finished_reducer_num = 0

        self.lock = Lock()
        self.mapper_res = [None] * 2000
        self.reducer_res = [None] * 2000

    def start_function_instance(self, work_type, work_id):
        returned_value = subprocess.check_output("wsk -i action invoke terasort -b -p type %d -p id %d" % (work_type, work_id), shell=True)
        if work_type == 0:
            self.mapper_res[work_id] = json.loads(returned_value)
            with lock:
                # print "Lock Acquired"
                self.finished_mapper_num += 1
        elif work_type == 1:
            self.reducer_res[work_id] = json.load(returned_value)
            with lock:
                self.finished_reducer_num += 1

    def start_mappers(self):
        for i in range(0, self.mapper_num):
            p = Thread(target=self.start_function_instance, args=(0, i))
            p.start()
        if self.finished_mapper_num == self.mapper_num:
            return

    def start_reducers(self):
        for i in range(0, self.reducer_num):
            p = Thread(target=self.start_function_instance, args=(1, i))
            p.start()
        if self.finished_reducer_num == self.reducer_num:
            return


if __name__ == "__main__":
    wsk_ts_test = wsk_terasort(1800, 1800)
    wsk_ts_test.start_mappers()
    for i in wsk_ts_test.mapper_res:
        print(i)


