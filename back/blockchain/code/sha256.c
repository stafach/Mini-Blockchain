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
 * The hash is based on the block's index, timestamp, data, previous_hash, and nonce.
 * The resulting hash is stored in block->hash.
 *
 @block : pointer to the block whose hash will be calculated
 */

void calculate_block_hash(Block *block) {
    char str_to_hash[512];
    char hash[HASH_SIZE];

    // Concatenation of the block fields
    snprintf(str_to_hash, sizeof(str_to_hash), "%d%ld%s%s%d",
             block->index,
             block->timestamp,
             block->data,
             block->previous_hash,
             block->nonce);

    // Calcul hash
    calculate_sha256(str_to_hash, hash);

    // Copuy result in the block
    strncpy(block->hash, hash, HASH_SIZE);
}
