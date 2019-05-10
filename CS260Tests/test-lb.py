#! /bin/python3

import subprocess
from threading import Thread
from threading import Lock
import os
import json
import random
import time
import string


if __name__ == "__main__":
    for i in range(0, 1000):
        subprocess.check_output("wsk -i action invoke %s" % ("/whisk.system/samples/wordCount"), shell=True)
