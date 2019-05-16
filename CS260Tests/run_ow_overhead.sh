# !/bin/bash

for fibNum in 1 2 4 8 16 32 64 128 256 ; do
    echo $fibNum
#    python test-overhead.py $fibNum >> ori_ow_results.txt
    python test-overhead.py $fibNum >> msg_ow_results.txt
done
