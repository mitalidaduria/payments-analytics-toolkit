import pandas as pd

from feature_engineering import generate_user_transaction_history_features


def test_generate_user_transaction_history_features():
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u1", "u2"],
            "timestamp": pd.to_datetime(
                ["2024-01-01 10:15:00", "2024-01-01 10:20:00", "2024-01-01 10:30:00", "2024-01-06 14:00:00"]
            ),
            "amount": [100, 200, 1000, 50],
            "merchant_category": ["grocery", "grocery", "electronics", "grocery"],
        }
    )

    result = generate_user_transaction_history_features(df)

    assert {"hour_of_day", "is_weekend", "user_txn_velocity_1h", "amount_zscore_vs_user_avg", "is_new_merchant_category"}.issubset(result.columns)
    assert result.loc[0, "hour_of_day"] == 10
    assert result.loc[3, "is_weekend"] == 1
    assert result.loc[0, "user_txn_velocity_1h"] == 0
    assert result.loc[2, "user_txn_velocity_1h"] >= 1
    assert result.loc[0, "amount_zscore_vs_user_avg"] == 0.0
    assert result.loc[2, "is_new_merchant_category"] == 1
