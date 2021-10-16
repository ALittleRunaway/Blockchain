"""The blockchain class"""
import hashlib
import json
from datetime import time
from urllib.parse import urlparse

import requests


class Blockchain(object):
    """The blockchain class"""
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """Creates the new block of blockchain"""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(time()),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """Creates a new transaction to go into the next mined Block"""
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        })

        return self.last_block["index"] + 1

    def register_node(self, address):
        """Add a new node to the list of nodes"""
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
         """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def valid_chain(self, chain):
        """Determine if a given blockchain is valid"""
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f"last block: {last_block}")
            print(f"block: {block}\n{'-'*10}\n")

            if block["previous_hash"] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is the Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

    @staticmethod
    def valid_proof(last_proof, proof):
        """Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?"""
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        """Creates a SHA-256 hash of a Block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
