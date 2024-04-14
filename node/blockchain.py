import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash, data=None):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'data': data}  # Add 'data' field for vote
        self.chain.append(block)
        return block

    def print_previous_block(self):
        return self.chain[-1]

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

app = Flask(__name__)

blockchain = Blockchain()

peer_nodes = set()

def validate_block(block):
    required_fields = ['index', 'timestamp', 'proof', 'previous_hash', 'data']
    if not all(field in block for field in required_fields):
        return False
    
    # You can add more specific validations for the 'data' field if needed
    
    previous_proof = block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    if proof != block['proof']:
        return False
    
    previous_hash = blockchain.hash(blockchain.chain[-1])
    if previous_hash != block['previous_hash']:
        return False
    
    return True

@app.route('/receive_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()
    received_block = block_data
    
    if validate_block(received_block):
        blockchain.chain.append(received_block)
        for node in peer_nodes:
            requests.post(node + '/receive_block', json=received_block)
        response = {'message': 'Block added to the blockchain'}
        return jsonify(response), 200
    else:
        response = {'message': 'Invalid block received'}
        return jsonify(response), 400

@app.route('/register_node', methods=['POST'])
def register_node():
    node_data = request.get_json()
    node_address = node_data.get('node_address')

    if not node_address:
        return "Invalid data", 400

    peer_nodes.add(node_address)
    return "Node registered successfully", 200

@app.route('/mine_block', methods=['GET'])
def mine_block():
    last_block = blockchain.chain[-1]
    previous_proof = last_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(last_block)
    
    # For simplicity, let's assume the vote data is received as a query parameter 'candidate'
    candidate = request.args.get('candidate')
    if not candidate:
        return "No candidate provided", 400
    
    data = {'voter': request.remote_addr, 'candidate': candidate}
    
    block = blockchain.create_block(proof, previous_hash, data)
    
    for node in peer_nodes:
        requests.post(node + '/receive_block', json=block)

    response = {'message': 'New block mined',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'data': block['data']}
    
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/valid', methods=['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)

    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
