# !/bin/bash

#bash ../ansible/mysetup_dist.sh
#for i in {1..10}; do
#    for fibNum in 1 2 4 8 16 32 64 128 ; do
#        echo $fibNum
#        python test-overhead.py $fibNum >> ./results/ow_overhead/msg_ow_results.txt
#    done
#done

#cd ..
#git checkout openwhisk-ori
#cd ./CS260Tests
#
#bash ../ansible/mysetup_dist.sh

#for i in {1..10}; do
for i in {1}; do
    for fibNum in 1 2 4 8 16 32 64 128 ; do
        echo $fibNum
        python test-overhead.py $fibNum >> ./results/ow_overhead/ori_ow_results.txt
    done
done
