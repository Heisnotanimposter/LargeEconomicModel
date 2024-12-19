import pandas as pd
from blockchain import Blockchain

if __name__ == "__main__":
    # Initialize the blockchain
    my_blockchain = Blockchain()

    # Load the enhanced transaction dataset (after sentiment analysis)
    transactions_path = "./LargeEconomicModel/Experiment/dataset/transactions_with_sentiment.csv"
    df = pd.read_csv(transactions_path)

    # For demonstration, let's add each transaction as a separate block.
    # In practice, you might batch multiple transactions into a single block.
    # Ensure that the required columns exist: 'transaction_id', 'description', 'category', etc.
    required_cols = ["transaction_id", "description", "category", "sentiment_label", "sentiment_score"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in transactions_with_sentiment.csv")

    # Convert each row into a dictionary to store in a block
    for _, row in df.iterrows():
        block_data = {
            "transaction_id": row["transaction_id"],
            "description": row["description"],
            "category": row["category"],
            "sentiment_label": row["sentiment_label"],
            "sentiment_score": row["sentiment_score"]
            # Add more fields as needed: token_id, from_id, to_id, amount, etc.
        }
        my_blockchain.add_block(block_data)

    # Check if the blockchain is valid
    if my_blockchain.is_chain_valid():
        print("Blockchain is valid.")
    else:
        print("Blockchain integrity compromised.")

    # Print a summary of the blockchain
    for i, block in enumerate(my_blockchain.chain):
        print(f"\n--- Block {i} ---")
        print(f"Timestamp: {block.timestamp}")
        print(f"Data: {block.data}")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")

import json

with open("./LargeEconomicModel/Experiment/dataset/blockchain_data.json", "w") as f:
    json.dump([block.__dict__ for block in my_blockchain.chain], f, default=str)