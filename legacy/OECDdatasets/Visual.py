import pandas as pd

# Load datasets into DataFrames
balance_of_payments_df = pd.read_csv('BalanceofPayments.csv')
g20_economic_lookout_df = pd.read_csv('G20EconomicLookout.csv')
weekly_tracker_df = pd.read_csv('OECDWeeklyTrackerofeconomicActivity.csv')

# Display the first few rows of each DataFrame to understand their structure
print("Balance of Payments Dataset:")
print(balance_of_payments_df.head())

print("\nG20 Economic Lookout Dataset:")
print(g20_economic_lookout_df.head())

print("\nWeekly Tracker of Economic Activity Dataset:")
print(weekly_tracker_df.head())

# Display information about each DataFrame to understand their structure and data types
print("\nBalance of Payments Dataset Info:")
print(balance_of_payments_df.info())

print("\nG20 Economic Lookout Dataset Info:")
print(g20_economic_lookout_df.info())

print("\nWeekly Tracker of Economic Activity Dataset Info:")
print(weekly_tracker_df.info())