import ctypes
import atexit
import os
from flask import Flask
from flask_restx import Api
import facade
from models import Blockchain
from routes import api as blocks_ns

app = Flask(__name__)
# configure the API with Swagger
api = Api(app, title='Blockchain API', version='1.0', description='Blockchain moteur C')

# Blockchain initialization
ma_bc = Blockchain()
ma_bc.difficulty = 3
ma_bc.length = 0

# Create the genesis block
facade.initialize(ctypes.byref(ma_bc))

facade.active_blockchain = ma_bc

api.add_namespace(blocks_ns, path='/blocks')

# Free the malloc of the blockchain
def cleanup():
    if facade.active_blockchain:
        print("\n[CLEANUP] Freeing Blockchain memory...")
        facade.free(ctypes.byref(facade.active_blockchain))
        print("[CLEANUP] Memory successfully released.")

# When close the server use cleanup function
atexit.register(cleanup)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
