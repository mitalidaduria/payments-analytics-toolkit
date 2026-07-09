import numpy as np
import pandas as pd


def perform_cohort_analysis(df, customer_id_col, date_col, amount_col=None):
    """Perform a basic cohort retention analysis for payment activity.

    Parameters
    ----------
    df : pandas.DataFrame
        Input payment transactions with customer identifiers and activity dates.
    customer_id_col : str
        Column containing the customer identifier.
    date_col : str
        Column containing the payment date.
    amount_col : str, optional
        Column containing the payment amount. If provided, the output includes
        aggregated revenue metrics per cohort and period.

    Returns
    -------
    pandas.DataFrame
        A long-form cohort table with one row per cohort-month and period.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "cohort_month",
                "period_number",
                "cohort_size",
                "active_customers",
                "retention_rate",
                "total_amount",
                "avg_amount_per_customer",
            ]
        )

    analysis_df = df.copy()
    analysis_df[date_col] = pd.to_datetime(analysis_df[date_col], errors="coerce")
    analysis_df = analysis_df.dropna(subset=[customer_id_col, date_col]).copy()

    if analysis_df.empty:
        return pd.DataFrame(
            columns=[
                "cohort_month",
                "period_number",
                "cohort_size",
                "active_customers",
                "retention_rate",
                "total_amount",
                "avg_amount_per_customer",
            ]
        )

    analysis_df["cohort_month"] = (
        analysis_df.groupby(customer_id_col)[date_col]
        .transform("min")
        .dt.to_period("M")
        .astype(str)
    )
    analysis_df["activity_month"] = analysis_df[date_col].dt.to_period("M")
    analysis_df["cohort_period"] = analysis_df["cohort_month"].astype("period[M]")

    cohort_sizes = (
        analysis_df[[customer_id_col, "cohort_month"]]
        .drop_duplicates()
        .groupby("cohort_month")
        .size()
        .rename("cohort_size")
        .reset_index()
    )

    analysis_df["period_number"] = (
        analysis_df["activity_month"] - analysis_df["cohort_period"]
    ).apply(lambda x: x.n if hasattr(x, "n") else 0)

    active_users = (
        analysis_df.groupby(["cohort_month", "period_number", customer_id_col])
        .size()
        .reset_index(name="activity_count")
        .groupby(["cohort_month", "period_number"])[customer_id_col]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )

    result = cohort_sizes.merge(active_users, on="cohort_month", how="left")
    result = result[result["period_number"].notna()]
    result["retention_rate"] = result["active_customers"] / result["cohort_size"]

    if amount_col is not None and amount_col in analysis_df.columns:
        amount_summary = (
            analysis_df.groupby(["cohort_month", "period_number"])[amount_col]
            .sum()
            .rename("total_amount")
            .reset_index()
        )
        result = result.merge(amount_summary, on=["cohort_month", "period_number"], how="left")
        result["avg_amount_per_customer"] = result["total_amount"] / result["active_customers"].replace(0, pd.NA)

    result = result.sort_values(["cohort_month", "period_number"]).reset_index(drop=True)
    return result


def generate_synthetic_transactions(
    n_customers=25,
    start_date="2024-01-01",
    months_span=6,
    max_periods=4,
    seed=42,
):
    """Generate synthetic payment transactions for cohort analysis."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp(start_date)
    records = []

    for customer_idx in range(1, n_customers + 1):
        cohort_month = start + pd.DateOffset(months=int(rng.integers(0, months_span)))
        active_months = [cohort_month]

        for period in range(1, max_periods):
            if rng.random() < (0.5 if period == 1 else 0.2):
                active_months.append(cohort_month + pd.DateOffset(months=period))

        for payment_month in active_months:
            amount = round(float(rng.integers(100, 500)) * (1 + 0.05 * len(active_months)), 2)
            records.append(
                {
                    "customer_id": f"C{customer_idx:03d}",
                    "payment_date": payment_month.strftime("%Y-%m-%d"),
                    "amount": amount,
                }
            )

    return pd.DataFrame(records).sort_values("payment_date").reset_index(drop=True)


def build_retention_matrix(cohort_result):
    """Convert a cohort analysis result into a retention matrix for reporting."""
    if cohort_result.empty:
        return pd.DataFrame(columns=["cohort_month", "cohort_size", "M0"])

    period_numbers = sorted(cohort_result["period_number"].dropna().astype(int).unique())
    matrix = (
        cohort_result.pivot_table(
            index="cohort_month",
            columns="period_number",
            values="retention_rate",
            aggfunc="max",
        )
        .reindex(columns=range(max(period_numbers) + 1), fill_value=0.0)
        .rename(columns=lambda value: f"M{value}")
    )

    cohort_sizes = (
        cohort_result[["cohort_month", "cohort_size"]]
        .drop_duplicates()
        .set_index("cohort_month")
    )

    matrix = cohort_sizes.join(matrix, how="left").reset_index()
    matrix = matrix[["cohort_month", "cohort_size", *[col for col in matrix.columns if col not in {"cohort_month", "cohort_size"}]]]
    return matrix.sort_values("cohort_month").reset_index(drop=True)


def format_retention_matrix_markdown(retention_matrix):
    """Render a retention matrix as a Markdown table."""
    if retention_matrix.empty:
        return "| cohort_month | cohort_size |"

    display = retention_matrix.copy()
    display["cohort_month"] = display["cohort_month"].astype(str)
    display["cohort_size"] = display["cohort_size"].astype(int)

    for column in display.columns:
        if column.startswith("M"):
            display[column] = display[column].apply(lambda value: f"{value:.0%}" if pd.notna(value) else "-")

    columns = display.columns.tolist()
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = ["| " + " | ".join([str(row[column]) for column in columns]) + " |" for _, row in display.iterrows()]
    return "\n".join([header, separator, *rows])


if __name__ == "__main__":
    transactions = generate_synthetic_transactions()
    cohort_result = perform_cohort_analysis(
        transactions,
        customer_id_col="customer_id",
        date_col="payment_date",
        amount_col="amount",
    )
    retention_matrix = build_retention_matrix(cohort_result)

    print("### Monthly cohort retention matrix")
    print(format_retention_matrix_markdown(retention_matrix))
