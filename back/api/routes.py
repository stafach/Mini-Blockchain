from flask_restx import Namespace, Resource, fields
from flask import jsonify, request
import facade
import ctypes
from models import Transaction

api = Namespace('blocks', description='block operation')

# Define Transaction model
transaction_model = api.model('Transaction', {
    'sender': fields.String(description='The person sending the coins', example='Alice'),
    'receiver': fields.String(description='The person receiving the coins', example='Bob'),
    'amount': fields.Float(description='The amount of coins', example=10.5)
})

# Define the Block model for input validation
block_model = api.model('Block', {
    'index': fields.Integer(description='The index of the block in the chain'),
    'timestamp': fields.Integer(description='Unix timestamp of the block'),
    'tx_count': fields.Integer(description='Number of transaction stored in the block'),
    'transactions': fields.List(fields.Nested(transaction_model), description='List of transactions in the block'),
    'hash': fields.String(description='SHA256 hash of the block'),
    'previous_hash': fields.String(description='Hash of the previous block'),
    'nonce': fields.Integer(description='The nonce used for mining')
})

# Define the model for add a block
add_block_model = api.model('Add', {
    'transactions': fields.List(fields.Nested(transaction_model), description='List of transactions')
})

@api.route('/')
class BlockList(Resource):
    @api.marshal_list_with(block_model) # Automatically converts objects to JSON
    def get(self):
        """Retrieve the complete blockchain"""
        chain_data = [] # Create empty list to add the entire blockchain

        # Retrieving each block
        for i in range(facade.active_blockchain.length):
            block_ptr = facade.active_blockchain.blocks[i]
            b = block_ptr.contents #accesses the content of each block
            

            transactions = [] # Create empty list for all transactions of the block
            for j in range (b.tx_count):
                transactions.append({
                "sender": b.tx[j].sender.decode('utf-8'), # Use utf-8 to convert bytes to string
                "receiver": b.tx[j].receiver.decode('utf-8'),
                "amount": b.tx[j].amount
            })
            
            # Add each fields to the list
            chain_data.append({
                "index": b.index,
                "timestamp": b.timestamp,
                "tx_count": b.tx_count,
                "transactions": transactions,
                "hash": b.hash.decode('utf-8'),
                "previous_hash": b.previous_hash.decode('utf-8'),
                "nonce": b.nonce
            })
            
        return chain_data
    
@api.route('/add')
class AddBlock(Resource):
    @api.expect(add_block_model)
    @api.response(400, 'Missing data field')
    @api.response(400, 'Failed to add block')
    @api.response(500, 'Internal error')
    @api.response(400, 'Failed to save block')
    @api.response(201, 'Block added')
    def post(self):
        """Add a block and mine it"""
        # Retrieves the data in JSON format
        data_json = request.json
        if not data_json or 'transactions' not in data_json:
            return {"error": "Missing transactions field"}, 400
        # Retrieves the transactions
        data_txs = data_json.get('transactions', [])
        
        if not data_txs:
            return {"error": "No transactions provided"}, 400
        if len(data_txs) > 5:
            return {"error": f"Too many ({len(data_txs)}) transactions (max 5)"}, 400
        

        try:
             # Create an array with all transactions
            txs_arrays = (Transaction * 5)()
            for i, tx_data in enumerate(data_txs):
                            txs_arrays[i].sender = tx_data['sender'][:49].encode('utf-8') # Use [:49] for no break the server
                            txs_arrays[i].receiver = tx_data['receiver'][:49].encode('utf-8')
                            txs_arrays[i].amount = float(tx_data['amount'])

            # Call add function
            result = facade.add(ctypes.byref(facade.active_blockchain), txs_arrays, len(data_txs))
            
            # Check the result
            if result != 0:
                return {"error": "Failed to add block"}, 400
        except Exception as e:
            return {"error": f"Internal error: {str(e)}"}, 500
        
        # Save the blockchain in json file
        try:
            save = facade.save_blockchain(facade.active_blockchain)

            # Check the result
            if save != 0:
                return {"error": "Failed to save the block"}, 400
        except Exception as e:
            return {"error": f"Internal error: {str(e)}"}, 500
        
        # Retrieves the hash of the block added
        last_block_ptr = facade.last_block(ctypes.byref(facade.active_blockchain))
        new_hash = last_block_ptr.contents.hash.decode('utf-8')
        
        return {
            "message": "Block added",
            "index": facade.active_blockchain.length - 1,
            "number of transaction": last_block_ptr.contents.tx_count,
            "hash": new_hash
        }, 201


@api.route('/validate')
class ValidateChain(Resource):
    @api.response(200, 'Blockchain is valid and untampered.')
    @api.response(400, 'Blockchain corruption detected!')
    def get(self):
        """Verifies the integrity of the blockchain"""
        # Call the function
        error_idx = ctypes.c_int(0)

        result = facade.chain_valid(ctypes.byref(facade.active_blockchain), ctypes.byref(error_idx))
        
        # Check the result
        if result == 0:
            return {
                "status": "Success",
                "message": "Blockchain is valid.",
                "length": facade.active_blockchain.length
            }, 200
        else:
            idx = error_idx.value
            return {
                "status": "Error",
                "message": f"Corruption detected at block index {idx} "
            }, 400
        