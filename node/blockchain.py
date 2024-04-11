# Python program to create Blockchain

# For timestamp
import datetime

# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain
import json

# For http requests to allow nodes to interact
import requests

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify, request


class Blockchain:

    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    # This function is created
    # to display the previous block
    def print_previous_block(self):
        return self.chain[-1]

    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1

        return True

# Creating the Web
# App using flask
app = Flask(__name__)

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Set to store addresses of other nodes in the network
peer_nodes = set()

# Add a new endpoint for receiving new blocks from other nodes
@app.route('/receive_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()
    received_block = json.loads(block_data)
    
    # Validate the received block
    if validate_block(received_block):
        # Add the block to the local blockchain
        blockchain.chain.append(received_block)
        
        # Propagate the received block to other nodes in the network
        for node in peer_nodes:
            requests.post(node + '/receive_block', json=received_block)
        
        response = {'message': 'Block added to the blockchain'}
        return jsonify(response), 200
    else:
        response = {'message': 'Invalid block received'}
        return jsonify(response), 400

# Add a new endpoint for registering new nodes in the network
@app.route('/register_node', methods=['POST'])
def register_node():
    node_data = request.get_json()
    node_address = node_data.get('node_address')

    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)
    return "Node registered successfully", 200

# Modify the mine_block endpoint to broadcast the newly mined block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # Mine the block as before...
    # After mining, broadcast the new block to other nodes in the network
    for node in peer_nodes:
        requests.get(node + '/receive_block', json=blockchain.chain[-1])
    
    return jsonify(response), 200

# Modify the display_chain endpoint to return the local blockchain
@app.route('/get_chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Check validity of blockchain

@app.route('/valid', methods=['GET'])
def valid():
	valid = blockchain.chain_valid(blockchain.chain)

	if valid:
		response = {'message': 'The Blockchain is valid.'}
	else:
		response = {'message': 'The Blockchain is not valid.'}
	return jsonify(response), 200


# Run the flask server locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)