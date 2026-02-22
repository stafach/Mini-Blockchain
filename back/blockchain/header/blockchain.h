#ifndef BLOCKCHAIN_H
#define BLOCKCHAIN_H

#include "block.h"

#define MAX_BLOCKS 1000

typedef struct Blockchain
{
    Block *blocks[MAX_BLOCKS];
    int length;
    int difficulty;
} Blockchain;


void init_blockchain(Blockchain *bc);
int add_block(Blockchain *bc, const char *data);
int is_chain_valid(const Blockchain *bc);
void mine_block(Block *block, int difficulty);
Block *get_last_block(Blockchain *bc);
void free_blockchain(Blockchain *bc);
void print_blockchain(const Blockchain *bc);

#endif
