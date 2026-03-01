import csv
import random
from datetime import datetime, timedelta

# Configuration
NUM_TRANSACTIONS = 1000

# Sample data
countries = ['India', 'USA', 'UK', 'UAE', 'Singapore', 'Australia', 'Canada', 'Germany']
merchant_types = ['retail', 'grocery', 'restaurant', 'online', 'travel', 'healthcare', 'education', 
                  'entertainment', 'utilities', 'automobile', 'jewelry', 'real_estate', 'business',
                  'crypto_exchange', 'investment']
currencies = ['USD', 'EUR', 'GBP', 'INR', 'AED', 'SGD']
transaction_types = ['transfer', 'payment', 'withdrawal', 'deposit']

# Risk distribution weights (most transactions should be low risk)
device_risk_distribution = [
    (0.1, 0.6),   # 60% low risk (0.0-0.3)
    (0.3, 0.25),  # 25% medium risk (0.3-0.6)
    (0.6, 0.1),   # 10% higher risk (0.6-0.8)
    (0.8, 0.05),  # 5% high risk (0.8-1.0)
]

# Transaction amount ranges
amount_ranges = [
    (100, 1000, 0.3),      # 30% small transactions
    (1000, 10000, 0.4),    # 40% medium
    (10000, 100000, 0.2),  # 20% large
    (100000, 500000, 0.08), # 8% very large
    (500000, 2000000, 0.02) # 2% extremely large
]

def get_random_amount():
    """Generate random amount based on distribution"""
    r = random.random()
    cumulative = 0
    for min_amt, max_amt, weight in amount_ranges:
        cumulative += weight
        if r <= cumulative:
            return round(random.uniform(min_amt, max_amt), 2)
    return round(random.uniform(100, 1000), 2)

def get_random_device_risk():
    """Generate random device risk score based on distribution"""
    r = random.random()
    cumulative = 0
    for min_risk, weight in device_risk_distribution:
        cumulative += weight
        if r <= cumulative:
            return round(random.uniform(min_risk, min_risk + 0.3), 2)
    return round(random.uniform(0, 0.3), 2)

def get_random_country():
    """Generate random country with India being most common"""
    r = random.random()
    if r < 0.6:  # 60% India
        return 'India'
    elif r < 0.75:  # 15% USA
        return 'USA'
    elif r < 0.85:  # 10% UK
        return 'UK'
    elif r < 0.92:  # 7% UAE
        return 'UAE'
    elif r < 0.97:  # 5% Singapore
        return 'Singapore'
    else:
        return random.choice(['Australia', 'Canada', 'Germany'])

def get_random_merchant_type(country):
    """Generate random merchant type based on country"""
    # Higher chance of crypto for non-India
    if country != 'India' and random.random() < 0.15:
        return 'crypto_exchange'
    return random.choice(merchant_types)

def get_timestamp(start_date, transaction_num):
    """Generate timestamp distributed over the period"""
    days_offset = transaction_num // 40  # Distribute over ~25 days
    hour = random.randint(9, 18)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return start_date + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)

# Generate transactions
start_date = datetime(2024, 1, 1)
transactions = []

for i in range(1, NUM_TRANSACTIONS + 1):
    transaction_id = f"TXN-{1000 + i}"
    user_id = f"user_{str(random.randint(1, 200)).zfill(3)}"
    amount = get_random_amount()
    currency = random.choice(currencies)
    country = get_random_country()
    merchant_type = get_random_merchant_type(country)
    device_risk_score = get_random_device_risk()
    timestamp = get_timestamp(start_date, i)
    trans_type = random.choice(transaction_types)
    description = f"Transaction {i}"
    recipient_account = f"ACC{random.randint(1000000000, 9999999999)}"
    sender_account = f"ACC{random.randint(1000000000, 9999999999)}"
    
    transactions.append({
        'transaction_id': transaction_id,
        'user_id': user_id,
        'amount': amount,
        'currency': currency,
        'country': country,
        'merchant_type': merchant_type,
        'device_risk_score': device_risk_score,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'transaction_type': trans_type,
        'description': description,
        'recipient_account': recipient_account,
        'sender_account': sender_account
    })

# Write to CSV
fieldnames = ['transaction_id', 'user_id', 'amount', 'currency', 'country', 'merchant_type', 
              'device_risk_score', 'timestamp', 'transaction_type', 'description', 
              'recipient_account', 'sender_account']

with open('finpol/backend/data/sample_transactions.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(transactions)

print(f"Generated {NUM_TRANSACTIONS} transactions successfully!")
