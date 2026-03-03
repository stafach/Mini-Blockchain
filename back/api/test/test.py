import pytest
import os
import json
from app import app
from facade import active_blockchain, load_blockchain
import ctypes

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_genesis_block_exists(client):
    """Verify that the blockchain starts with at least one block (Genesis)"""
    response = client.get('/blocks/')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['index'] == 0

def test_add_block(client):
    """Checks the addition and mining of a new block"""
    payload = {"data": "Test Transaction"}
    response = client.post('/blocks/add', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == "Block added"
    assert "hash" in data

def test_data_overflow(client):
    """Checks behavior when input data exceeds maximum size"""
    # Create big string
    giant_string = "A" * 5000 
    payload = {"data": giant_string}
    
    response = client.post('/blocks/add', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code in [400] 


def test_blockchain_validation(client):
    """Verifies that the route validate confirms the integrity of the chain"""
    response = client.get('/blocks/validate')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['status'] == "Success"



def test_tamper_detection(client):
    """
    Test if /validate detects that the blockchain is corrupted
    """
    # Add a block and save it
    client.post('/blocks/add', data=json.dumps({"data": "Safe data"}), content_type='application/json')

    # Modify the data of the blockchain
    db_file = "blockchain.json"
    with open(db_file, 'r') as f:
        content = json.load(f)
    content[-1]['data'] = "HACKED DATA"
    with open(db_file, 'w') as f:
        json.dump(content, f)

    #load the backup with the modified data
    load_blockchain(active_blockchain, db_file)

    # checks if the blockchain is valid
    response = client.get('/blocks/validate')
    
    assert response.status_code == 400
    assert "Corruption detected" in response.get_json()['message']


def test_recreate_overflow(client):
    """Check that recreate_blockchain handles excessively long data"""
    db_file = "blockchain.json"
    
    # Verify that the blockchain is initialized
    client.get('/blocks/') 

    # Modify last block with data > DATA_SIZE
    with open(db_file, 'r') as f:
        content = json.load(f)
    content[-1]['data'] = "B" * 5000 
    
    with open(db_file, 'w') as f:
        json.dump(content, f)
    
    # load_blockchain calls recreate_blockchain
    result = load_blockchain(active_blockchain, db_file)
    
    # Verify that the engine has refused rebuilding
    assert result is False
    