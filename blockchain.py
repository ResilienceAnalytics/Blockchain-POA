import hashlib
import json
from time import time
from flask import Flask, jsonify, request

class Blockchain:
    """
    A simple implementation of a Blockchain to record session data.

    Attributes:
        chain (list): A list to store the chain of blocks.
        current_data (list): A list to store the current session data to be added to the next block.
    """
    def __init__(self):
        self.chain = []
        self.current_data = []

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block in the blockchain.

        Args:
            proof (int): The proof given by the Proof of Authority algorithm.
            previous_hash (str, optional): Hash of the previous block. Defaults to None.

        Returns:
            dict: The new block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': self.current_data,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_data = []
        self.chain.append(block)
        return block

    def new_data(self, session_data):
        """
        Add a new session data to the list of data.

        Args:
            session_data (dict): The session data to be added.

        Returns:
            int: The index of the block that will hold this data.
        """
        self.current_data.append({
            'users': session_data['users'],
            'data': session_data.get('data', []),
            'dh_parameters': session_data['dh_parameters'],
            'server_public_key': session_data['server_public_key'],
            'receiver_public_key': session_data['receiver_public_key'],
            'sender_public_key': session_data['sender_public_key'],
            'sender_zkp_status': session_data.get('sender_zkp_status', 'Pending'),
            'receiver_zkp_status': session_data.get('receiver_zkp_status', 'Pending'),
            'sender_balance': session_data.get('sender_balance', 0),
            'receiver_balance': session_data.get('receiver_balance', 0),
            'authentification': session_data.get('authentification', 'Pending'),
            'Sufficient_amount': session_data.get('Sufficient_amount', 'Pending'),
            'sender_wallet_hash': session_data.get('sender_wallet_hash', ''),
            'receiver_wallet_hash': session_data.get('receiver_wallet_hash', '')
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.

        Args:
            block (dict): Block.

        Returns:
            str: The hash of the block.
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Get the last block in the chain.

        Returns:
            dict: The last block in the chain.
        """
        return self.chain[-1]

    def proof_of_authority(self, last_proof):
        """
        Simulate a Proof of Authority mechanism (for demonstration purposes).

        Args:
            last_proof (int): The proof of the previous block.

        Returns:
            int: The new proof.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validate the proof (for demonstration purposes, a simple condition).

        Args:
            last_proof (int): The proof of the previous block.
            proof (int): The current proof.

        Returns:
            bool: True if the proof is valid, False otherwise.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Instantiation of our node
app = Flask(__name__)

# Instantiation of the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    """
    Mine a new block.
    """
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_authority(last_proof)

    # Reward for finding the proof
    blockchain.new_data({
        'users': '0',
        'data': [],
        'dh_parameters': '',
        'server_public_key': '',
        'receiver_public_key': '',
        'sender_public_key': '',
        'sender_zkp_status': 'Completed',
        'receiver_zkp_status': 'Completed',
        'sender_balance': 0,
        'receiver_balance': 0,
        'authentification': 'Completed',
        'Sufficient_amount': 'Completed',
        'sender_wallet_hash': '',
        'receiver_wallet_hash': ''
    })

    # Forge the new block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'data': block['data'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Create a new transaction.
    """
    values = request.get_json()

    # Check that the required fields are in the POST data
    required = ['users', 'data', 'dh_parameters', 'server_public_key', 'receiver_public_key', 'sender_public_key']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_data(values)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Return the full blockchain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
