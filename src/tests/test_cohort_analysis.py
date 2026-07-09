import pandas as pd

from cohort_analysis import (
    build_retention_matrix,
    perform_cohort_analysis,
)


def test_perform_cohort_analysis():
    data = [
        {"customer_id": "A", "payment_date": "2024-01-01", "amount": 100},
        {"customer_id": "A", "payment_date": "2024-02-01", "amount": 150},
        {"customer_id": "B", "payment_date": "2024-01-15", "amount": 200},
        {"customer_id": "C", "payment_date": "2024-02-10", "amount": 250},
        {"customer_id": "C", "payment_date": "2024-03-05", "amount": 125},
    ]
    df = pd.DataFrame(data)

    result = perform_cohort_analysis(
        df,
        customer_id_col="customer_id",
        date_col="payment_date",
        amount_col="amount",
    )

    jan_cohort = result[(result["cohort_month"] == "2024-01") & (result["period_number"] == 1)]
    feb_cohort = result[(result["cohort_month"] == "2024-02") & (result["period_number"] == 1)]

    assert len(result) == 4
    assert jan_cohort.iloc[0]["retention_rate"] == 0.5
    assert feb_cohort.iloc[0]["retention_rate"] == 1.0
    assert jan_cohort.iloc[0]["active_customers"] == 1
    assert feb_cohort.iloc[0]["active_customers"] == 1


def test_build_retention_matrix():
    data = [
        {"customer_id": "A", "payment_date": "2024-01-01", "amount": 100},
        {"customer_id": "A", "payment_date": "2024-02-01", "amount": 150},
        {"customer_id": "B", "payment_date": "2024-01-15", "amount": 200},
    ]
    df = pd.DataFrame(data)
    result = perform_cohort_analysis(df, customer_id_col="customer_id", date_col="payment_date")
    matrix = build_retention_matrix(result)

    assert matrix.loc[0, "cohort_size"] == 2
    assert matrix.loc[0, "M1"] == 0.5
