# !/bin/bash

KB=1024
MB=1048576

#for dataSize in 64 1024 262144 524288 1048576 2097152 4194304 8388608 16777216 33554432 67108864 134217728 ; do
#    echo $dataSize
##    echo $dataSize >> ./results/data_trans/msg_data_trans_datasize.txt
##    echo $dataSize >> ./results/data_trans/redis_data_trans_datasize.txt
#    for i in {1..10}
#    do
#        python test-data-transferal.py $dataSize func-data-transferal 1 >> ./results/data_trans/msg_data_trans_datasize.txt
#        python test-data-transferal.py $dataSize func-data-transferal-redis 1 >> ./results/data_trans/redis_data_trans_datasize.txt
#    done
#done


for sendNum in 1 2 4 8 16 32 64 128 ; do
    echo $sendNum
    echo $sendNum >> ./results/data_trans/msg_data_trans_sendnum.txt
    echo $sendNum >> ./results/data_trans/redis_data_trans_sendnum.txt
    for i in {1..10}
    do
        python test-data-transferal.py 64 func-data-transferal $sendNum >> ./results/data_trans/msg_data_trans_sendnum.txt
        python test-data-transferal.py 64 func-data-transferal-redis $sendNum >> ./results/data_trans/redis_data_trans_sendnum.txt
    done
done
