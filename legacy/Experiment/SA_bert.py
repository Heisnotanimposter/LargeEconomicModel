#pip install transformers torch pandas
#pip install matplotlib

import os
import torch
import pandas as pd
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SiEBERTSentimentAnalyzer:
    def __init__(self, model_name="siebert/sentiment-roberta-large-english"):
        if os.path.isdir(model_name):
            print(f"Loading model from local directory: {model_name}")
        else:
            print(f"Loading model from Hugging Face model hub: {model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def analyze_sentiment(self, text: str) -> dict:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1).tolist()[0]
        negative_score, positive_score = scores
        label = "positive" if positive_score > negative_score else "negative"
        score = max(positive_score, negative_score)
        return {"label": label, "score": score}

if __name__ == "__main__":
    # Initialize sentiment analyzer
    analyzer = SiEBERTSentimentAnalyzer()
    
    # Paths to datasets
    base_path = "./LargeEconomicModel/Experiment/dataset"
    transactions_path = os.path.join(base_path, "transactions.csv")
    individuals_path = os.path.join(base_path, "individuals.csv")
    tokens_path = os.path.join(base_path, "tokens.csv")
    reference_data_path = os.path.join(base_path, "reference_data.csv")
    ce_profiles_path = os.path.join(base_path, "ce_profiles.json")
    
    # Load main transaction data
    df = pd.read_csv(transactions_path)
    if 'description' not in df.columns:
        raise ValueError("The transactions.csv file does not have a 'description' column.")

    # Apply sentiment analysis to the description column
    df['sentiment_result'] = df['description'].apply(lambda x: analyzer.analyze_sentiment(x) if pd.notnull(x) else {"label": None, "score": None})
    df['sentiment_label'] = df['sentiment_result'].apply(lambda d: d['label'] if d else None)
    df['sentiment_score'] = df['sentiment_result'].apply(lambda d: d['score'] if d else None)
    df.drop(columns='sentiment_result', inplace=True)

    # Load additional datasets
    individuals_df = pd.read_csv(individuals_path)
    tokens_df = pd.read_csv(tokens_path)
    reference_df = pd.read_csv(reference_data_path)
    
    # Load CE profiles
    with open(ce_profiles_path, 'r') as f:
        ce_profiles = json.load(f)
    
    # MERGE EXAMPLES:
    # 1. Merge individuals data:
    #    If the transactions contain a 'to_id' or 'from_id' that matches 'individual_id' in individuals.csv
    #    We can merge to add demographic or income info. For demonstration, let's assume 'to_id' is the receiver of tokens.
    if 'to_id' in df.columns and 'individual_id' in individuals_df.columns:
        df = df.merge(individuals_df, left_on='to_id', right_on='individual_id', how='left', suffixes=('', '_indiv'))
    
    # 2. Merge tokens data:
    #    If each transaction references a 'token_id' that appears in tokens.csv, we can merge token info.
    if 'token_id' in df.columns and 'token_id' in tokens_df.columns:
        df = df.merge(tokens_df[['token_id', 'current_owner_id']], on='token_id', how='left', suffixes=('', '_token'))

    # 3. Merge reference data on category:
    #    If the transactions have a 'category' field that matches 'category_name' in reference_data.csv
    if 'category' in df.columns and 'category_name' in reference_df.columns:
        df = df.merge(reference_df, left_on='category', right_on='category_name', how='left', suffixes=('', '_ref'))
    
    # Optionally, we can inspect the CE profiles data and add a column that references a spending profile:
    # For instance, if we have a 'spending_profile_reference' in the merged df (from individuals.csv),
    # we can add a column showing the top category that the CE profile suggests.
    if 'spending_profile_reference' in df.columns:
        def top_ce_category(profile_key):
            if profile_key in ce_profiles:
                profile = ce_profiles[profile_key]
                # Get the category with the highest probability
                return max(profile, key=profile.get)
            return None
        
        df['ce_top_category'] = df['spending_profile_reference'].apply(top_ce_category)

    # Now df contains sentiment, individuals info, token info, reference data, and CE profile insights.
    # Save updated DataFrame
    output_path = os.path.join(base_path, "transactions_enhanced.csv")
    df.to_csv(output_path, index=False)
    print(f"Data enhancement completed. Results saved to: {output_path}")

    # Additional Analysis (Optional):
    # For example, compute average sentiment scores by category.
    if 'category' in df.columns:
        category_sentiment = df.groupby('category')['sentiment_score'].mean()
        print("Average sentiment score by category:")
        print(category_sentiment)

    # Or compare the distribution of spending categories with reference targets if that data is available:
    if 'category' in df.columns and 'target_percent' in df.columns:
        # Count how often each category appears
        category_counts = df['category'].value_counts(normalize=True) * 100
        print("\nActual spending distribution (in %):")
        print(category_counts)

        print("\nReference target distribution (from reference_data.csv):")
        ref_distribution = reference_df.set_index('category_name')['target_percent']
        print(ref_distribution)
        
        # Compare actual vs target
        comparison_df = pd.DataFrame({
            'actual_percent': category_counts,
            'target_percent': ref_distribution
        })
        comparison_df['difference'] = comparison_df['actual_percent'] - comparison_df['target_percent']
        print("\nComparison of actual vs target distribution:")
        print(comparison_df)

        import matplotlib.pyplot as plt

        # Plot actual vs target percentages
        fig, ax = plt.subplots(figsize=(10, 6))

        comparison_df_sorted = comparison_df.sort_values('category') if 'category' in comparison_df.index.names else comparison_df.sort_values(by=comparison_df.index.name)

        # Extract data for plotting
        categories = comparison_df_sorted.index
        actual_values = comparison_df_sorted['actual_percent']
        target_values = comparison_df_sorted['target_percent']

        bar_width = 0.35
        x = range(len(categories))

        # Create bar chart
        ax.bar(x, actual_values, width=bar_width, label='Actual', alpha=0.7)
        ax.bar([i + bar_width for i in x], target_values, width=bar_width, label='Target', alpha=0.7)

        # Formatting
        ax.set_xlabel('Category')
        ax.set_ylabel('Percentage')
        ax.set_title('Comparison of Actual vs Target Spending Distribution')
        ax.set_xticks([i + bar_width/2 for i in x])
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()
        plt.show()

        # Optionally, plot the differences
        fig_diff, ax_diff = plt.subplots(figsize=(10, 6))
        differences = comparison_df_sorted['difference']
        ax_diff.bar(categories, differences, color='orange', alpha=0.7)
        ax_diff.axhline(y=0, color='black', linewidth=1)
        ax_diff.set_xlabel('Category')
        ax_diff.set_ylabel('Difference (Actual - Target)')
        ax_diff.set_title('Difference Between Actual and Target Distribution')
        ax_diff.set_xticklabels(categories, rotation=45, ha='right')

        plt.tight_layout()
        plt.show()