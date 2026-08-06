# Payments-analytics-toolkit

# Payments-analytics-toolkit

Modular Python framework for transaction analytics, churn modeling, and payment funnel metrics.

---

##  Key Capabilities

* **Cohort Retention Analysis:** Monthly tracking of payment user retention, churn dynamics, and repeat transaction behavior (`cohort_analysis.py`).
* **Feature Engineering Pipeline:** Extraction of transaction-history features, velocity metrics, and payment frequency indicators (`feature_engineering.py`).
* **SQL Profiling Sandbox:** Local database profiling setup (`day2.db`) for transaction data validation.

---

##  Quickstart

```bash
# Clone the repository
git clone [https://github.com/mitalidaduria/payments-analytics-toolkit.git](https://github.com/mitalidaduria/payments-analytics-toolkit.git)
cd payments-analytics-toolkit

# Run cohort analysis script
python cohort_analysis.py

# Run feature engineering pipeline
python feature_engineering.py
