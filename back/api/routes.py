from flask_restx import Namespace, Resource, fields
from flask import jsonify, request
import facade
import ctypes

api = Namespace('blocks', description='block operation')

# Define the block model for input validation
block_model = api.model('Block', {
    'index': fields.Integer(description='The index of the block in the chain'),
    'timestamp': fields.Integer(description='Unix timestamp of the block'),
    'data': fields.String(description='Data stored in the block'),
    'hash': fields.String(description='SHA256 hash of the block'),
    'previous_hash': fields.String(description='Hash of the previous block'),
    'nonce': fields.Integer(description='The nonce used for mining')
})

add_block_model = api.model('Add', {
    'data': fields.String(description='Data stored in the block'),
})

@api.route('/')
class BlockList(Resource):
    @api.marshal_list_with(block_model) # Automatically converts objects to JSON
    def get(self):
        """Retrieve the complete blockchain"""
        chain_data = []

        for i in range(facade.active_blockchain.length):
            block_ptr = facade.active_blockchain.blocks[i]
            b = block_ptr.contents
            
            chain_data.append({
                "index": b.index,
                "timestamp": b.timestamp,
                "data": b.data.decode('utf-8'), # Conversion bytes -> string
                "hash": b.hash.decode('utf-8'),
                "previous_hash": b.previous_hash.decode('utf-8'),
                "nonce": b.nonce
            })
            
        return chain_data
    
@api.route('/add')
class AddBlock(Resource):
    @api.expect(add_block_model)
    @api.response(201, 'Block added successfully')
    @api.response(400, 'Invalid data or mining failed')
    @api.response(500, 'Internal error')
    def post(self):
        """Add a block and mine it"""
        data_json = request.json
        if not data_json or 'data' not in data_json:
            return {"error": "Missing 'data' field"}, 400
        
        data_string = data_json.get('data')
        
        try:
            result = facade.add(ctypes.byref(facade.active_blockchain), data_string.encode('utf-8'))
            
            if result != 0:
                return {"error": "Failed to add block"}, 400
        except Exception as e:
            return {"error": f"Internal error: {str(e)}"}, 500
        
        last_block_ptr = facade.last_block(ctypes.byref(facade.active_blockchain))
        new_hash = last_block_ptr.contents.hash.decode('utf-8')
        
        return {
            "message": "Block added",
            "index": facade.active_blockchain.length - 1,
            "hash": new_hash
        }, 201


@api.route('/validate')
class ValidateChain(Resource):
    @api.response(200, 'Blockchain is valid and untampered.')
    @api.response(400, 'Blockchain corruption detected!')
    def get(self):
        """Vérifie l'intégrité de la blockchain via le moteur C"""
        # On appelle la fonction C
        result = facade.chain_valid(ctypes.byref(facade.active_blockchain))
        
        if result == 0:
            return {
                "status": "Success",
                "message": "Blockchain is valid and untampered.",
                "length": facade.active_blockchain.length
            }, 200
        else:
            return {
                "status": "Error",
                "message": "Blockchain corruption detected!"
            }, 400
        