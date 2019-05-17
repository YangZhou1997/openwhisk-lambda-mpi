# !/bin/bash

KB=1024
MB=1048576

for dataSize in 64 1*$KB 256*$KB 512*$KB 1*$MB 2$MB 4$MB 8$MB 16$MB 32$MB 64$MB 128$MB ; do
    echo $dataSize
#    echo $dataSize >> ./results/data_trans/msg_data_trans_datasize.txt
#    echo $dataSize >> ./results/data_trans/redis_data_trans_datasize.txt
    for i in {1..10}
    do
        python test-data-transferal.py $dataSize func-data-transferal 1 >> ./results/data_trans/msg_data_trans_datasize.txt
        python test-data-transferal.py $dataSize func-data-transferal-redis 1 >> ./results/data_trans/redis_data_trans_datasize.txt
    done
done


for sendNum in 1 2 4 8 16 32 64 128 ; do
    echo $sendNum
#    echo $sendNum >> ./results/data_trans/msg_data_trans_sendnum.txt
#    echo $sendNum >> ./results/data_trans/redis_data_trans_sendnum.txt
    for i in {1..10}
    do
        python test-data-transferal.py 64 func-data-transferal $sendNum >> ./results/data_trans/msg_data_trans_sendnum.txt
        python test-data-transferal.py 64 func-data-transferal-redis $sendNum >> ./results/data_trans/redis_data_trans_sendnum.txt
    done
done
