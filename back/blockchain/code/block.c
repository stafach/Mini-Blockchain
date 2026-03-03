#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include "../header/block.h"
#include "../header/blockchain.h"

/*
 * Creates the first block of the blockchain (Genesis Block)
 */
Block *create_genesis_block(void)
{
    // Allocate memory for the block
    Block *block = malloc(sizeof(Block));
    if (!block)
        return NULL;

    // Fill in fields
    block->index = 0;
    block->timestamp = time(NULL);
    strncpy(block->data, "Genesis Block", DATA_SIZE - 1);
    block->data[DATA_SIZE - 1] = '\0';  // ensure null-termination
    strncpy(block->previous_hash, "0", HASH_SIZE - 1);
    block->previous_hash[HASH_SIZE - 1] = '\0';
    block->nonce = 0;
    block->prev = NULL;

    // Calculate hash for the genesis block
    calculate_block_hash(block);

    return block;
}

/**
 * Performs Proof-of-Work by incrementing the nonce until the hash
 * satisfies the difficulty (hash starts with required number of zeros)
 *
 * block: pointer to the block to mine
 * difficulty: number of leading zeros required in the hash
 */

void mine_block(Block *block, int difficulty)
{
    char prefix[HASH_SIZE];

    for (int i = 0; i < difficulty; i++)
        prefix[i] = '0';
    prefix[difficulty] = '\0';

    block->nonce = 0;

    while (1)
    {
        calculate_block_hash(block);

        if (strncmp(block->hash, prefix, difficulty) == 0)
            break;

        block->nonce++;
    }

    printf("Block mined! Nonce: %d, Hash: %s\n", block->nonce, block->hash);
}


/**
* Init the Blockchain with the first block (genesis)
*
* bc: pointer to the block  */

void init_blockchain(Blockchain *bc)
{
    if (!bc)
        return;

    // Verify it's the first block
    if (bc->length != 0)
    {
        fprintf(stderr, "Blockchain already initialized\n");
        return;
    }

    Block *genesis = create_genesis_block();
    // Verify genesis block is create
    if (!genesis)
    {
        fprintf(stderr, "Failed to create genesis block\n");
        return;
    }

    mine_block(genesis, bc->difficulty);
    bc->blocks[0] = genesis;
    bc->length = 1;
}

/**
* Add a block to the blockchain
*
* bc: the blockchain
* data: the data of the block
*/
int add_block(Blockchain *bc, const char *data)
{
    if (!bc || !data || bc->length >= MAX_BLOCKS || strlen(data) >= DATA_SIZE)
        return -1;

    if (bc->length <= 0)
    {
        fprintf(stderr, "Cannot add block: blockchain is empty. Initialize genesis block first.\n");
        return -1;
    }
    Block *new_block = malloc(sizeof(Block));
    if (!new_block)
        return -1;

    new_block->index = bc->length;
    new_block->timestamp = time(NULL);
    strncpy(new_block->data, data, DATA_SIZE - 1); // Copy the data in the block
    new_block->data[DATA_SIZE - 1] = '\0'; // Ensure last char is \0
    
    Block *prev = get_last_block(bc); //Get the last block of the blockchain
    strncpy(new_block->previous_hash, prev->hash, HASH_SIZE - 1); // Copy the hash of last block in the new block
    new_block->previous_hash[HASH_SIZE - 1] = '\0'; // Ensure last char is \0

    new_block->prev = prev; // Chain the new block to the previous one


    new_block->nonce = 0;
    mine_block(new_block, bc->difficulty); // Mine the block hash

    bc->blocks[bc->length] = new_block; // Add the new block to the blockchain
    bc->length++; // Iterate th length

    return 0;
}

/**
* Ensure the blockchain is valid
*
* bc: the blokchain
*/
int is_chain_valid(const Blockchain *bc, int *error_index)
{
    if (!bc)
        return -1;
    int i = 0;

    while (i < bc->length)
    {
        Block *current = bc->blocks[i];

        char original_hash[HASH_SIZE];
        strncpy(original_hash, current->hash, HASH_SIZE);
        
        // Use a tmp block for not modify current block
        Block tmp_block = *current;
        calculate_block_hash(&tmp_block);
        
        if (strcmp(tmp_block.hash, original_hash) != 0)
        {
            fprintf(stderr, "Invalid data at block %d: Hash doesn't match content!\n", i);
            *error_index = i;
            return -1;
        }

        if (i == 0)
        {
            if (strcmp(bc->blocks[i]->previous_hash, "0") != 0)
            {
                fprintf(stderr, "Error previous hash genesis block");
                *error_index = i;
                return -1;
            }
        }
        else
        {
            if (strcmp(bc->blocks[i]->previous_hash, bc->blocks[i-1]->hash) != 0)
            {
                fprintf(stderr, "Error previous hash at block %d", i);
                *error_index = i;
                return -1;
            }
        }
        i++;
    }
    return 0;
}

/**
* Get the last block of the blockchain
*
* bc: The blockchain
 */
Block *get_last_block(Blockchain *bc)
{
    if (!bc)
        return NULL;

    return bc->blocks[bc->length - 1];
}

/**
* Free the memory of the blockchain
*
* bc: The blochckain
*/
void free_blockchain(Blockchain *bc)
{
    if (!bc) return;

    for (int i = 0; i < bc->length; i++)
        free(bc->blocks[i]);

    bc->length = 0;
}

/**
 * Adds a block from existing data (used for loading from disk)
 * without re-mining it.
 */
int recreate_blockchain(Blockchain *bc, int index, long timestamp, const char *data, 
                  const char *hash, const char *prev_hash, int nonce)
{
    if (!bc || bc->length >= MAX_BLOCKS || strlen(data) >= DATA_SIZE)
        return -1;

    Block *new_block = malloc(sizeof(Block));
    if (!new_block)
        return -1;

    new_block->index = index;
    new_block->timestamp = timestamp;
    
    strncpy(new_block->data, data, DATA_SIZE - 1);
    new_block->data[DATA_SIZE - 1] = '\0';
    
    strncpy(new_block->hash, hash, HASH_SIZE - 1);
    new_block->hash[HASH_SIZE - 1] = '\0';
    
    strncpy(new_block->previous_hash, prev_hash, HASH_SIZE - 1);
    new_block->previous_hash[HASH_SIZE - 1] = '\0';

    new_block->nonce = nonce;
    

    if (index != 0)
        new_block->prev = bc->blocks[bc->length - 1];
    else
        new_block->prev = NULL;

    bc->blocks[bc->length] = new_block;
    bc->length++;

    return 0;
}
