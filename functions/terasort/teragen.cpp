#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAPPER_NUM 1800
#define REDUCER_NUM 1800
#define STR_NUM_PER_MAPPER (1024 * 1024)
#define STR_LEN 32

using namespace std;

void get_random_string(char *buf, int num_bytes)
{
    int i = 0;
    for(; i < num_bytes / 3 + 1; i++)
    {
        uint temp = rand();
        //printf("%x %x %x %x\n", *(char*)(&temp) & 0xff, *((char*)(&temp) + 1) & 0xff, *((char*)(&temp) + 2) & 0xff, *((char*)(&temp) + 3) & 0xff);
        //printf("%x %x %x %x\n", temp & 0xff, (temp >> 8) & 0xff, (temp >> 16) & 0xff, (temp >> 24) & 0xff);
        memcpy(buf + i * 3, (char *)(&temp), 3);
    }
}

char buf[STR_NUM_PER_MAPPER * STR_LEN + 3];
int main()
{
    for(int i = 0; i < MAPPER_NUM; i++)
    {
        srand(time(0));
        get_random_string(buf, STR_NUM_PER_MAPPER * STR_LEN);
    
        char filename[128];
        sprintf(filename, "/users/yangzhou/openwhisk/addrMap/teradata/src_data/%s%dM_%d.dat", "__random_bytes_", STR_LEN, i);
        FILE *fp = fopen(filename, "w");
        fwrite(buf, sizeof(char), STR_NUM_PER_MAPPER * STR_LEN, fp);
        fclose(fp);
    }
    return 0;
}
