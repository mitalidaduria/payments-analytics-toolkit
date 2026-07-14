# Feature Engineering Analysis

## Feature-to-business-rule matrix

| Feature | Business rule / requirement | Fraud signal encoded | Example output value | Interpretation |
| --- | --- | --- | --- | --- |
| `hour_of_day` | The system shall preserve the transaction hour from the event timestamp as a contextual signal for unusual activity patterns. | Unusual hours may indicate automation or account takeover. | 10, 14 | The sample shows daytime activity for user `u1` and a later daytime transaction for `u2`. |
| `is_weekend` | The system shall flag transactions that occur on weekend days so weekend behavior can be compared against a user's typical schedule. | Weekend activity may be less typical and can signal compromise. | 0, 1 | `1` flags the weekend transaction for `u2`. |
| `user_txn_velocity_1h` | The system shall calculate a rolling 60-minute transaction count per `user_id`, updated in real time, and flag counts exceeding 5 as elevated velocity. | A burst of transactions in a short window often indicates rapid abuse. | 0, 1, 2 | The sample shows increasing local velocity for `u1` across consecutive transactions. |
| `amount_zscore_vs_user_avg` | The system shall compare each transaction amount to the user's historical average and report the standardized deviation as a measure of anomalous spend. | Amounts far from a user's own baseline may indicate card-testing or stolen credentials. | 0.0, 17.0 | The large `1000` transaction for `u1` produces a very high z-score. |
| `is_new_merchant_category` | The system shall flag transactions that use a merchant category not previously seen for the user as potentially unfamiliar or suspicious behavior. | New merchant categories can indicate unfamiliar spend. | 1, 0 | `u1`'s first transaction in `electronics` is flagged as new. |

## Sample output table

| user_id | timestamp | amount | merchant_category | hour_of_day | is_weekend | user_txn_velocity_1h | amount_zscore_vs_user_avg | is_new_merchant_category |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| u1 | 2024-01-01 10:15:00 | 100 | grocery | 10 | 0 | 0 | 0.0 | 1 |
| u1 | 2024-01-01 10:20:00 | 200 | grocery | 10 | 0 | 1 | 0.0 | 0 |
| u1 | 2024-01-01 10:30:00 | 1000 | electronics | 10 | 0 | 2 | 17.0 | 1 |
| u2 | 2024-01-06 14:00:00 | 50 | grocery | 14 | 1 | 0 | 0.0 | 1 |

## Analysis summary

- The third transaction for `u1` stands out most strongly because it combines a high amount, a new merchant category, and elevated transaction history context.
- The weekend indicator is only activated for the `u2` sample transaction.
- The velocity feature increases across the first three rows for the same user, reflecting the rolling 60-minute history calculation.