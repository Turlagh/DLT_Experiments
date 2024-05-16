import datetime
import hashlib
import json
import random
from flask import Flask, jsonify, request

class TangleLedger:
    def __init__(self):
        self.tangle = {}  # Dictionary to store transactions
        self.nodes = set()  # Set to store the addresses of other nodes

    def add_node(self, address):
        self.nodes.add(address)

    def add_transaction(self, transaction):
        # Select two previous transactions to reference (tips)
        prev_transactions = self.select_tips()

        # Validate the transaction by checking the approval of the selected tips
        if not self.validate_transaction(prev_transactions):
            return "Transaction validation failed", 400

        # Add transaction to the tangle
        transaction_id = hashlib.sha256(json.dumps(transaction).encode()).hexdigest()
        self.tangle[transaction_id] = transaction

        return "Transaction added successfully", 201

    def select_tips(self):
        # Randomly select two tips from the tangle
        tips = random.sample(list(self.tangle.keys()), 2)
        return tips

    def validate_transaction(self, prev_transactions):
        if len(self.tangle) < 2:
            return False  # Not enough transactions to validate

        # Check approval of the selected previous transactions
        return all(tx in self.tangle for tx in prev_transactions)

app = Flask(__name__)
tangle = TangleLedger()

@app.route('/add_node', methods=['POST'])
def add_node():
    values = request.get_json()
    node = values.get('node')
    if node is None:
        return "Error: Please supply a valid node address", 400

    tangle.add_node(node)

    response = {
        'message': 'New node has been added',
        'total_nodes': list(tangle.nodes),
    }
    return jsonify(response), 201

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    values = request.get_json()
    required_fields = ['sender', 'receiver']
    if not all(field in values for field in required_fields):
        return 'Missing values', 400

    transaction = {
        'sender': values['sender'],
        'receiver': values['receiver'],
        'timestamp': str(datetime.datetime.now())
    }

    # Add transaction to the Tangle
    result, status_code = tangle.add_transaction(transaction)

    response = {'message': result}
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
