#include "../header/block.h"
#include <openssl/sha.h>
#include <string.h>
#include <stdio.h>

/**
* Computes the SHA256 hash of the input string.
* The resulting hash will be 64 hexadecimal characters + '\0'.
*
@input : string of characters
@output : hash SHA256
*/

void calculate_sha256(const char *input, char *output)
{
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;

    SHA256_Init(&sha256);
    SHA256_Update(&sha256, input, strlen(input));
    SHA256_Final(hash, &sha256);

    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[64] = '\0';
}

/**
 * Computes the SHA256 hash of a blockchain block.
 * The hash is based on the block's index, timestamp, transaction, previous_hash, and nonce.
 * The resulting hash is stored in block->hash.
 *
 @block : pointer to the block whose hash will be calculated
 */

void calculate_block_hash(Block *block) {
    char str_to_hash[4096];
    char tx_str[512];
    char hash[HASH_SIZE];

    // initialize the buffer
    str_to_hash[0] = '\0';

    // Concatenation of the block fields
    snprintf(str_to_hash, sizeof(str_to_hash), "%d%ld%d%s%d",
             block->index,
             block->timestamp,
             block->tx_count,
             block->previous_hash,
             block->nonce);
    
    // Concatenation of the transaction
    for (int i = 0; i < block->tx_count; i++)
    {
        snprintf(tx_str, sizeof(tx_str), "%s%s%.2f",
                 block->tx[i].sender,
                 block->tx[i].receiver,
                 block->tx[i].amount);
        strcat(str_to_hash, tx_str);
    }
    // Calcul hash
    calculate_sha256(str_to_hash, hash);

    // Copuy result in the block
    strncpy(block->hash, hash, HASH_SIZE - 1);
    block->hash[HASH_SIZE - 1] = '\0';
}
