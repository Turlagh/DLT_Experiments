# Simple python implementation showing Blockchain across a set of local container nodes

# Import relevant libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()  # Set to store the addresses of other nodes
        self.create_block(proof=1, previous_hash='0') # Create first block and set its hash to "0"

    # Sets data type of the block
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'transactions': self.transactions,
                'proof': proof,
                'previous_hash': previous_hash}
        self.transactions = []  # Reset transactions list once block created
        self.chain.append(block)
        return block

    def print_previous_block(self):
        return self.chain[-1]

    # Logic for the proof of work functionality
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

    # Logic for determining validity of chain
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

    #function to allow new addresses in the form of ip addresses onto the node
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #Function to propogate created blocks to other nodes
    def add_transaction(self, voter_id, candidate_id):
        self.transactions.append({
            'voter_id': voter_id,
            'candidate_id': candidate_id,
        })

        #broadcast to other nodes
        for node in self.nodes:
            url = f'http://{node}/add_transaction'
            requests.post(url, json={
                'voter_id': voter_id,
                'candidate_id': candidate_id
            })

    def broadcast_block(self, block):
        """
        Broadcast a mined block to all other nodes in the network

        :param block: The mined block to be broadcasted
        """
        for node in self.nodes:
            url = f'http://{node}/receive_block'
            requests.post(url, json=block)


# Creating the Web
# App using flask
app = Flask(__name__)

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Check if there are transactions to include in the block
    if not blockchain.transactions:
        return jsonify({'message': 'No transactions to mine. Add transactions first.'}), 400
    
    # Create the new block with transactions
    block = blockchain.create_block(proof, previous_hash)

    # Broadcast the mined block to other nodes
    blockchain.broadcast_block(block)

    response = {'message': 'A block is MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'transactions': block['transactions'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}

    return jsonify(response), 200

# Display blockchain in json format
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

# Add a new node to the network
@app.route('/register_node', methods=['POST'])
def register_node():
    values = request.get_json()

    if values is None:
        return "Error: Please supply a valid list of nodes", 400

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/receive_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()

    if block_data is None:
        return "Error: Please supply valid block data", 400

    # Validate the received block
    is_valid = blockchain.chain_valid([block_data])

    if is_valid:
        blockchain.chain.append(block_data)
        response = {'message': 'Block received and validated successfully'}
        return jsonify(response), 200
    else:
        response = {'message': 'Received block is not valid'}
        return jsonify(response), 400

# Add a new transaction (vote)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    values = request.get_json()

    # Check if the required fields are in the POST'ed data
    required_fields = ['voter_id', 'candidate_id']
    if not all(field in values for field in required_fields):
        return 'Missing values', 400

    # Add the transaction to the blockchain
    blockchain.add_transaction(values['voter_id'], values['candidate_id'])

    response = {'message': 'Transaction added successfully'}
    return jsonify(response), 201

# Run the flask server locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
