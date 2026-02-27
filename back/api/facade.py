import ctypes
from models import Block, Blockchain

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
chain_valid.argtypes = [ctypes.POINTER(Blockchain)]
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
