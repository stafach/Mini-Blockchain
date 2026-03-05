#ifndef BLOCK_H
#define BLOCK_H

#include <time.h>
#include <stddef.h>

#define HASH_SIZE 65
#define MAX_TRANSACTIONS 5

typedef struct Transaction
{
    char sender[50];
    char receiver[50];
    float amount;
} Transaction;

typedef struct Block
{
    int index;
    time_t timestamp;
    int tx_count;
    Transaction tx[MAX_TRANSACTIONS];
    char previous_hash[HASH_SIZE];
    char hash[HASH_SIZE];
    int nonce;
} Block;

void calculate_sha256(const char *input, char *output);
void calculate_block_hash(Block *block);
Block *create_genesis_block(void);
#endif