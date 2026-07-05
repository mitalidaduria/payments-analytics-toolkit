dq_config = {
    'amount': {'min': 1, 'max': 500000, 'null_pct_max': 0},
    'gateway': {'allowed_values': ['Razorpay', 'PayU', 'Stripe'], 'null_pct_max': 0},
    'timestamp': {'format': 'datetime', 'null_pct_max': 0}
}