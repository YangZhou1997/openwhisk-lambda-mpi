# !/bin/bash

for fibNum in 1 2 4 8 16 32 64 128 ; do
    echo $fibNum
#    python test-overhead.py $fibNum >> ./results/ow_overhead/ori_ow_results.txt
    python test-overhead.py $fibNum >> ./results/ow_overhead/msg_ow_results.txt
done
