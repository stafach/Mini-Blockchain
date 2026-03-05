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
    # Create transactions
    payload = {
        "transactions": [
            {"sender": "Alice", "receiver": "Bob", "amount": 50.0},
            {"sender": "Charlie", "receiver": "Alice", "amount": 10.0}
            ]
        }
    # Try to add the block
    response = client.post('/blocks/add', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    # Retrieves the response
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['message'] == "Block added"
    assert "hash" in data


def test_transaction_count_overflow(client):
    """Checks for rejection if more than 5 transactions per block are allowed."""
    # Create 6 transactions
    too_many_txs = [{"sender": "A", "receiver": "B", "amount": 1.0}] * 6
    payload = {"transactions": too_many_txs}
    
    # Try to add the block
    response = client.post('/blocks/add', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 400
    assert "Too many (6) transactions (max 5)" in response.get_json()['error']


def test_sender_receiver_string_overflow(client):
    """Checks the behavior when sender or receiver exceeds 50 characters"""
    # Create a string more than the char[50] defined in C
    long_name = "A" * 60
    payload = {
        "transactions": [
            {"sender": long_name, "receiver": "Bob", "amount": 10.0}
        ]
    }
    # Try to add the block
    response = client.post('/blocks/add', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code in [201, 400]

def test_blockchain_validation(client):
    """Verifies that the route validate confirms the integrity of the chain"""
    response = client.get('/blocks/validate')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['status'] == "Success"


def test_tamper_detection_in_transactions(client):
    """Checks if transaction corruption is detected"""
    # Add a valid block
    payload = {"transactions": [{"sender": "Alice", "receiver": "Bob", "amount": 50.0}]}
    client.post('/blocks/add', data=json.dumps(payload), content_type='application/json')

    # Manually corrupt the JSON file by changing the amount
    db_file = "blockchain.json"
    with open(db_file, 'r') as f:
        content = json.load(f)
    
    # modify the amount of the last transaction in the last block
    content[-1]['transactions'][0]['amount'] = 999999.0 
    
    with open(db_file, 'w') as f:
        json.dump(content, f)

    # Reload the corrupted blockchain
    load_blockchain(active_blockchain, db_file)

    # Verify the validation
    response = client.get('/blocks/validate')
    assert response.status_code == 400
    assert "Corruption detected" in response.get_json()['message']


def test_recreate_invalid_tx_count(client):
    """Checks that load_blockchain fails if the JSON is inconsistent (tx_count > 5)"""
    db_file = "blockchain.json"
    
    with open(db_file, 'r') as f:
        content = json.load(f)
    
    # forces a tx_count that is impossible for the C engine
    content[-1]['tx_count'] = 10 
    
    with open(db_file, 'w') as f:
        json.dump(content, f)
    
    result = load_blockchain(active_blockchain, db_file)
    
    # The C engine (recreate_blockchain) must return -1, so load_blockchain returns False
    assert result is False
