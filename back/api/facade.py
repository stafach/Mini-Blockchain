import ctypes
from models import Block, Blockchain, Transaction
import json
import os

# retrieves the folder where the facade.py file is located
base_dir = os.path.dirname(os.path.abspath(__file__))
#built the path to the .so relative to the project
lib_path = os.path.join(base_dir, "../blockchain/code/blockchain.so")
blockchain = ctypes.CDLL(lib_path)

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
add.argtypes = [ctypes.POINTER(Blockchain), ctypes.POINTER(Transaction), ctypes.c_int]
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

# Verify is blockchain is active
active_blockchain = None


# Save the blockchain in a json file
def save_blockchain(bc, filename="blockchain.json"):
    chain_data = [] # Create empty list for save all the blockchain

    # accesses each block
    for i in range(bc.length):
        b = bc.blocks[i].contents

        # Create list with all transactions of the block
        tx_list = []
        for j in range(b.tx_count):
            tx_list.append({
                "sender": b.tx[j].sender.decode('utf-8'),
                "receiver": b.tx[j].receiver.decode('utf-8'),
                "amount": b.tx[j].amount
            })

        # Add all the data to the empty list
        chain_data.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "tx_count": b.tx_count,
            "transactions": tx_list, # Add the list of the transactions
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
    ctypes.c_int,
    ctypes.POINTER(Transaction), 
    ctypes.c_char_p, 
    ctypes.c_char_p, 
    ctypes.c_int
    ]
recreate_bc.restype = ctypes.c_int

# Recreate the blockchain with the json file
def load_blockchain(bc, filename="blockchain.json"):
    # Check the json file exist
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

        # Create an array with all transactions of the block for C langage
        tx_array = (Transaction * 5)()
        for i, tx_data in enumerate(b['transactions']):
            tx_array[i].sender = tx_data['sender'].encode('utf-8')
            tx_array[i].receiver = tx_data['receiver'].encode('utf-8')
            tx_array[i].amount = tx_data['amount']

        res = recreate_bc(
            ctypes.byref(bc),
            b['index'],
            b['timestamp'],
            b['tx_count'],
            tx_array,
            b['hash'].encode('utf-8'),
            b['previous_hash'].encode('utf-8'),
            b['nonce']
            )
        
        if res == -1:
            print(f"Error: recreation failed for block {b['index']}")
            return False

    print(f"Successfully restored {len(data)} blocks from {filename}")
    return True
