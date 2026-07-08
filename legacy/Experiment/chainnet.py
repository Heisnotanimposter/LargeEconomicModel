import hashlib
import json
import time

class Block:
    def __init__(self, data, previous_hash=''):
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Combine the timestamp, data, and previous hash into a unique string
        block_string = str(self.timestamp) + json.dumps(self.data, sort_keys=True) + self.previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        # Create the genesis block
        genesis_data = {"note": "Genesis Block"}
        self.chain = [Block(genesis_data, previous_hash="0")]

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        # The previous hash comes from the last block in the chain
        previous_hash = self.get_last_block().hash
        new_block = Block(data, previous_hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            # Check current block hash
            if current_block.hash != current_block.calculate_hash():
                return False
            # Check if current block’s previous hash matches the previous block’s hash
            if current_block.previous_hash != previous_block.hash:
                return False
        return True