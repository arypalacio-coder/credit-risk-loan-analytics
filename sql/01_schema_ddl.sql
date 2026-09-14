-- ============================================================================
-- CREDIT RISK & LOAN PORTFOLIO ANALYTICS: DIMENSIONAL SCHEMA (STAR SCHEMA)
-- Compatible with DuckDB / PostgreSQL / SQLite
-- ============================================================================

-- 1. Dimension Tables
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    monthly_income DECIMAL(12, 2) NOT NULL,
    credit_score INTEGER NOT NULL,
    credit_score_band VARCHAR(20) NOT NULL,
    employment_type VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    collateral_type VARCHAR(50) NOT NULL,
    min_term_months INTEGER NOT NULL,
    max_term_months INTEGER NOT NULL,
    base_annual_rate DECIMAL(6, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year_num INTEGER NOT NULL,
    quarter_num INTEGER NOT NULL,
    month_num INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    is_month_end BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_loan (
    loan_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    origination_date DATE NOT NULL,
    origination_year_month VARCHAR(7) NOT NULL,
    original_principal DECIMAL(14, 2) NOT NULL,
    annual_interest_rate DECIMAL(6, 4) NOT NULL,
    term_months INTEGER NOT NULL,
    monthly_installment DECIMAL(12, 2) NOT NULL,
    initial_credit_score INTEGER NOT NULL,
    initial_risk_grade VARCHAR(5) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

-- 2. Fact Tables
CREATE TABLE IF NOT EXISTS fct_loan_monthly_snapshot (
    snapshot_id VARCHAR(50) PRIMARY KEY,
    snapshot_date_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    loan_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    months_on_books INTEGER NOT NULL,
    outstanding_principal DECIMAL(14, 2) NOT NULL,
    accrued_interest DECIMAL(12, 2) NOT NULL,
    days_past_due INTEGER NOT NULL,
    delinquency_bucket VARCHAR(20) NOT NULL,
    is_par30 BOOLEAN NOT NULL,
    is_par60 BOOLEAN NOT NULL,
    is_par90 BOOLEAN NOT NULL,
    is_npl BOOLEAN NOT NULL,
    loan_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (snapshot_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (loan_id) REFERENCES dim_loan(loan_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

CREATE TABLE IF NOT EXISTS fct_daily_repayment (
    repayment_id VARCHAR(50) PRIMARY KEY,
    payment_date_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    loan_id INTEGER NOT NULL,
    principal_paid DECIMAL(12, 2) NOT NULL,
    interest_paid DECIMAL(12, 2) NOT NULL,
    fees_paid DECIMAL(12, 2) NOT NULL,
    total_paid DECIMAL(12, 2) NOT NULL,
    days_past_due_at_payment INTEGER NOT NULL,
    FOREIGN KEY (payment_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (loan_id) REFERENCES dim_loan(loan_id)
);