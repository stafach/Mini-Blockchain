import ctypes
from models import Block, Blockchain
import json
import os

blockchain = ctypes.CDLL('/Users/chermatmustapha/Mini-Blockchain/back/blockchain/code/blockchain.so')

# Genesis
create_genesis = blockchain.create_genesis_block
create_genesis.argtypes = []
create_genesis.restype = ctypes.POINTER(Block)

# Mine block
mine = blockchain.mine_block
mine.argtypes = [ctypes.POINTER(Block), ctypes.c_int]
mine.restype = None

# Initialize blockchain
initialize = blockchain.init_blockchain
initialize.argtypes = [ctypes.POINTER(Blockchain)]
initialize.restype = None

# Add block
add = blockchain.add_block
add.argtypes = [ctypes.POINTER(Blockchain), ctypes.c_char_p]
add.restype = ctypes.c_int

# Is chain valid
chain_valid = blockchain.is_chain_valid
chain_valid.argtypes = [ctypes.POINTER(Blockchain), ctypes.POINTER(ctypes.c_int)]
chain_valid.restype = ctypes.c_int

# Get last block
last_block = blockchain.get_last_block
last_block.argtypes = [ctypes.POINTER(Blockchain)]
last_block.restype = ctypes.POINTER(Block)

# Free blockchain
free = blockchain.free_blockchain
free.argtypes = [ctypes.POINTER(Blockchain)]
free.restype = None

# Print the blockchain
def print_full_blockchain(bc):
    print(f"\n--- BLOCKCHAIN STATUS (Length: {bc.length}) ---")
    
    for i in range(bc.length):
        block_ptr = bc.blocks[i] # accesses all blocks
        block = block_ptr.contents # accesses the content of each block pointer
        
        print(f"Block #{block.index}")
        print(f"  Timestamp: {block.timestamp}")
        print(f"  Data:      {block.data.decode('utf-8')}")
        print(f"  Hash:      {block.hash.decode('utf-8')}")
        print(f"  Prev Hash: {block.previous_hash.decode('utf-8')}")
        print(f"  Nonce:     {block.nonce}")
        print("-" * 30)

# Verify is blockchain is active
active_blockchain = None


# Save the blockchain in a json file
def save_blockchain(bc, filename="blockchain.json"):
    chain_data = []
    for i in range(bc.length):
        b = bc.blocks[i].contents
        chain_data.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "data": b.data.decode('utf-8'),
            "hash": b.hash.decode('utf-8'),
            "previous_hash": b.previous_hash.decode('utf-8'),
            "nonce": b.nonce
        })
    
    try:
        with open(filename, 'w') as f:
            json.dump(chain_data, f, indent=4)
        print(f"Blockchain saved to {filename}")
        return 0
    except Exception:
        return -1

# Recreate
recreate_bc = blockchain.recreate_blockchain
recreate_bc.argtypes = [
    ctypes.POINTER(Blockchain), 
    ctypes.c_int, 
    ctypes.c_long, 
    ctypes.c_char_p, 
    ctypes.c_char_p, 
    ctypes.c_char_p, 
    ctypes.c_int
    ]
recreate_bc.restype = ctypes.c_int

# Recreate the blockchain with the json file
def load_blockchain(bc, filename="blockchain.json"):
    if not os.path.exists(filename):
        return False
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    if not data:
        return False
    
    #clear the new blockchain
    free(bc)
    bc.length = 0

    for b in data:
            recreate_bc(
                ctypes.byref(bc),
                b['index'],
                b['timestamp'],
                b['data'].encode('utf-8'),
                b['hash'].encode('utf-8'),
                b['previous_hash'].encode('utf-8'),
                b['nonce']
            )

    print(f"Successfully restored {len(data)} blocks from {filename}")
    return True
