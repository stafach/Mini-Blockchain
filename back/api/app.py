import ctypes
import atexit
import os
from flask import Flask, send_from_directory
from flask_restx import Api
import facade
from models import Blockchain
from routes import api as blocks_ns
from flask_cors import CORS


# Create path to front directory
FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../front"))


app = Flask(__name__)
CORS(app)

# Routes for frontend
@app.route('/')
def serve_index():
    """Serves the blockchain's main page"""
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serves CSS, JS files and other pages (mine.html)"""
    return send_from_directory(FRONTEND_FOLDER, path)


# configure the API with Swagger
api = Api(app, title='Blockchain API', version='1.0', description='Blockchain engine', doc='/swagger')

# Blockchain initialization
ma_bc = Blockchain()
ma_bc.difficulty = 3
ma_bc.length = 0

# json file with the blockchain
DB_FILE = "blockchain.json"

# Verify if the file exist
if os.path.exists(DB_FILE):
    print(f"Load the blockchain from ({DB_FILE}) file")
    facade.load_blockchain(ma_bc, DB_FILE)
else:
    print("No backup, blockchain initialization")
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
