import hashlib
import json
import time
import pandas as pd

class Block:
    def __init__(self, transaction_list, previous_block_hash):
        """
        Represents a block in the blockchain.
        
        Parameters:
            transaction_list (list): A list of transaction strings.
            previous_block_hash (str): The hash of the previous block in the chain.
        """
        self.timestamp = time.time()
        self.transaction_list = transaction_list
        self.previous_block_hash = previous_block_hash
        self.block_hash = self.calculate_block_hash()

    def calculate_block_hash(self):
        """
        Calculate the SHA-256 hash of the block’s contents:
        (transactions + previous_block_hash + timestamp)
        """
        # Combine all transactions into one string, separated by '-'
        transactions_str = '-'.join(self.transaction_list)
        # Create a block string that includes transactions, previous hash, and timestamp
        block_string = transactions_str + '-' + self.previous_block_hash + '-' + str(self.timestamp)
        # Compute the SHA-256 hash
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        """
        Initialize a new blockchain with a Genesis block.
        """
        # Genesis block’s previous_hash can be something like '0' or 'initial_string'
        genesis_block = Block(transaction_list=["Genesis Block"], previous_block_hash="initial_string")
        self.chain = [genesis_block]

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, transaction_list):
        """
        Add a new block with the given transaction list to the blockchain.
        
        Parameters:
            transaction_list (list): A list of transaction strings to be stored in the new block.
        """
        previous_hash = self.get_last_block().block_hash
        new_block = Block(transaction_list, previous_hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Verify the integrity of the blockchain by checking each block’s hash 
        and comparing it to the stored previous_block_hash in the subsequent block.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Recalculate the current block’s hash and compare
            if current_block.block_hash != current_block.calculate_block_hash():
                print("Block", i, "has been tampered with.")
                return False

            # Compare the previous_block_hash with the previous block’s actual hash
            if current_block.previous_block_hash != previous_block.block_hash:
                print("Block", i, "previous hash does not match.")
                return False

        return True


if __name__ == "__main__":
    # Example usage with static transactions:
    my_blockchain = Blockchain()

    # Suppose we have some transactions
    t1 = "Anna sends 2 NC to Mike"
    t2 = "Bob sends 4.1 NC to Mike"
    t3 = "Mike sends 3.2 NC to Bob"
    t4 = "Daniel sends 0.3 NC to Anna"
    t5 = "Mike sends 1 NC to Charlie"
    t6 = "Mike sends 5.4 NC to Daniel"

    # Add blocks to the blockchain
    my_blockchain.add_block([t1, t2])
    my_blockchain.add_block([t3, t4])
    my_blockchain.add_block([t5, t6])

    # Validate the chain
    print("Is the blockchain valid?", my_blockchain.is_chain_valid())

    # Print the chain
    for i, block in enumerate(my_blockchain.chain):
        print(f"\n--- Block {i} ---")
        print("Timestamp:", block.timestamp)
        print("Transactions:", block.transaction_list)
        print("Previous Hash:", block.previous_block_hash)
        print("Hash:", block.block_hash)


    # Example of integrating with your CSV-based transaction data:
    # After running sentiment analysis and other processing, you have a CSV of transactions.
    # Each row in `transactions_with_sentiment.csv` can be converted into a transaction string.
    """
    df = pd.read_csv("./LargeEconomicModel/Experiment/dataset/transactions_with_sentiment.csv")
    # For demonstration, we’ll add only a few transactions at a time into a block.
    # In practice, you might batch them differently.
    
    # Convert rows to transaction strings:
    # Assume df has columns like 'transaction_id', 'description', 'category', 'sentiment_label', 'sentiment_score'
    transactions_batch = []
    for idx, row in df.iterrows():
        tx_str = f"ID: {row['transaction_id']} | Desc: {row['description']} | Cat: {row['category']} | Sentiment: {row['sentiment_label']} ({row['sentiment_score']})"
        transactions_batch.append(tx_str)
        # Every N transactions, add a block
        if len(transactions_batch) == 5:  # Example: every 5 transactions
            my_blockchain.add_block(transactions_batch)
            transactions_batch = []

    # If there's a remainder not forming a full batch
    if transactions_batch:
        my_blockchain.add_block(transactions_batch)

    print("After adding CSV transactions, is the blockchain still valid?", my_blockchain.is_chain_valid())
    """