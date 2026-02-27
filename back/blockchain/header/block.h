#ifndef BLOCK_H
#define BLOCK_H

#include <time.h>
#include <stddef.h>

#define HASH_SIZE 65
#define DATA_SIZE 256


typedef struct Block
{
    int index;
    time_t timestamp;
    char data[DATA_SIZE];
    char previous_hash[HASH_SIZE];
    char hash[HASH_SIZE];
    int nonce;
    struct Block *prev;
} Block;

void calculate_sha256(const char *input, char *output);
void calculate_block_hash(Block *block);
Block *create_genesis_block(void);
#endif