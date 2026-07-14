import pandas as pd


def generate_user_transaction_history_features(df):
    """Add transaction-history fraud features for each user transaction row.

    From business rule to feature — the translation
    ---------------------------------------------
    - hour_of_day: The system shall preserve the transaction hour from the event
      timestamp as a contextual signal for unusual activity patterns.
    - is_weekend: The system shall flag transactions that occur on weekend days
      so weekend behavior can be compared against a user's typical schedule.
    - user_txn_velocity_1h: The system shall calculate a rolling 60-minute
      transaction count per user_id, updated in real time, and flag counts
      exceeding 5 as elevated velocity.
    - amount_zscore_vs_user_avg: The system shall compare each transaction amount
      to the user's historical average and report the standardized deviation as a
      measure of anomalous spend.
    - is_new_merchant_category: The system shall flag transactions that use a
      merchant category not previously seen for the user as potentially unfamiliar
      or suspicious behavior.

    Parameters
    ----------
    df : pandas.DataFrame
        Transaction data containing at least user_id, timestamp, amount, and
        merchant_category columns.

    Returns
    -------
    pandas.DataFrame
        Input data with fraud-oriented behavioral features appended.
    """
    transaction_df = df.copy()

    if "user_id" not in transaction_df.columns:
        raise KeyError("Input data must include a 'user_id' column")
    if "timestamp" not in transaction_df.columns:
        raise KeyError("Input data must include a 'timestamp' column")
    if "amount" not in transaction_df.columns:
        raise KeyError("Input data must include an 'amount' column")
    if "merchant_category" not in transaction_df.columns:
        raise KeyError("Input data must include a 'merchant_category' column")

    transaction_df["timestamp"] = pd.to_datetime(transaction_df["timestamp"], errors="coerce")
    transaction_df = transaction_df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    # Fraud signal: transactions at unusual hours can indicate account takeover or automation.
    transaction_df["hour_of_day"] = transaction_df["timestamp"].dt.hour

    # Fraud signal: weekend activity can be less typical for some users and may signal compromise.
    transaction_df["is_weekend"] = transaction_df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)

    # Fraud signal: a burst of transactions inside a short window often points to rapid abuse.
    velocity = (
        transaction_df.groupby("user_id", group_keys=False)
        .rolling("60min", on="timestamp")
        .count()[["amount"]]
        .groupby(level=0)
        .shift(1)
        .fillna(0)
        .astype(int)
    )
    transaction_df["user_txn_velocity_1h"] = (
        velocity.reset_index(level=0, drop=True)
        .reindex(transaction_df.index)
        .fillna(0)["amount"]
        .astype(int)
    )

    # Fraud signal: amounts far from a user's own baseline can indicate card-testing or stolen credentials.
    expanding_mean = (
        transaction_df.groupby("user_id")["amount"]
        .expanding()
        .mean()
        .reset_index(level=0, drop=True)
        .shift(1)
        .fillna(0.0)
    )
    expanding_std = (
        transaction_df.groupby("user_id")["amount"]
        .expanding()
        .std(ddof=0)
        .reset_index(level=0, drop=True)
        .shift(1)
        .replace(0, pd.NA)
    )
    transaction_df["amount_zscore_vs_user_avg"] = (
        (transaction_df["amount"] - expanding_mean) / expanding_std
    ).fillna(0.0)

    # Fraud signal: a merchant category never seen before for a user can indicate unfamiliar spend.
    transaction_df["is_new_merchant_category"] = (
        transaction_df.groupby("user_id")["merchant_category"]
        .transform(lambda values: values.ne(values.shift()).astype(int))
        .fillna(1)
        .astype(int)
    )

    return transaction_df


if __name__ == "__main__":
    sample_df = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u1", "u2"],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01 10:15:00",
                    "2024-01-01 10:20:00",
                    "2024-01-01 10:30:00",
                    "2024-01-06 14:00:00",
                ]
            ),
            "amount": [100, 200, 1000, 50],
            "merchant_category": ["grocery", "grocery", "electronics", "grocery"],
        }
    )

    result = generate_user_transaction_history_features(sample_df)
    print(
        result[
            [
                "user_id",
                "timestamp",
                "amount",
                "merchant_category",
                "hour_of_day",
                "is_weekend",
                "user_txn_velocity_1h",
                "amount_zscore_vs_user_avg",
                "is_new_merchant_category",
            ]
        ].to_string(index=False)
    )
