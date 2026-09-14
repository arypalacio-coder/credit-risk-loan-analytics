# Data Dictionary: Credit Risk & Loan Portfolio Analytics

## 1. Dimensional Architecture Overview
This project uses a Kimball star schema modeled in DuckDB, consisting of four dimension tables and two fact tables designed for monthly portfolio monitoring, delinquency analysis, and daily repayment tracking.

---

## 2. Table Specifications

### Dim_Date (\dim_date\)
* **Grain:** One record per calendar day.
* **Primary Key:** \date_id\ (INTEGER, format YYYYMMDD).

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| date_id | INTEGER | No | Surrogate key in YYYYMMDD format. |
| full_date | DATE | No | Standard ISO calendar date. |
| year_num | INTEGER | No | Calendar year (e.g., 2024, 2025). |
| quarter_num | INTEGER | No | Calendar quarter (1 to 4). |
| month_num | INTEGER | No | Calendar month index (1 to 12). |
| month_name | VARCHAR(20) | No | Full month name (e.g., January). |
| year_month | VARCHAR(7) | No | Period string in YYYY-MM format. |
| is_month_end | BOOLEAN | No | Boolean flag indicating the last calendar day of the month. |

---

### Dim_Product (\dim_product\)
* **Grain:** One record per loan product configuration.
* **Primary Key:** \product_id\.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| product_id | INTEGER | No | Unique product identifier. |
| product_name | VARCHAR(50) | No | Commercial name of the credit product. |
| product_category | VARCHAR(50) | No | Category (e.g., Unsecured, Secured, Commercial). |
| collateral_type | VARCHAR(50) | No | Collateral requirement (e.g., None, Vehicle, Asset). |
| min_term_months | INTEGER | No | Minimum allowable contract duration in months. |
| max_term_months | INTEGER | No | Maximum allowable contract duration in months. |
| base_annual_rate | DECIMAL(6,4)| No | Base annual nominal interest rate before risk spread. |

---

### Dim_Customer (\dim_customer\)
* **Grain:** One record per unique borrower.
* **Primary Key:** \customer_id\.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| customer_id | INTEGER | No | Unique borrower identifier. |
| customer_name | VARCHAR(100)| No | Anonymized borrower name/code. |
| age | INTEGER | No | Borrower age at profile setup. |
| monthly_income | DECIMAL(12,2)| No | Verified monthly income in USD. |
| credit_score | INTEGER | No | Bureau credit score (range 300-850). |
| credit_score_band| VARCHAR(20) | No | Credit tier: Excellent, Good, Fair, Subprime. |
| employment_type| VARCHAR(50) | No | Employment status (Corporate, Self-Employed, etc.).|
| region | VARCHAR(50) | No | Geographic operating region. |

---

### Dim_Loan (\dim_loan\)
* **Grain:** One record per originated credit contract.
* **Primary Key:** \loan_id\.
* **Foreign Keys:** \customer_id\ references \dim_customer\, \product_id\ references \dim_product\.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| loan_id | INTEGER | No | Unique loan contract identifier. |
| customer_id | INTEGER | No | Foreign key to borrower. |
| product_id | INTEGER | No | Foreign key to credit product. |
| origination_date| DATE | No | Disbursal date. |
| origination_year_month | VARCHAR(7) | No | Disbursal cohort in YYYY-MM format. |
| original_principal | DECIMAL(14,2)| No | Initial disbursed credit amount. |
| annual_interest_rate | DECIMAL(6,4)| No | Effective annual interest rate (base + risk spread). |
| term_months | INTEGER | No | Total contract duration in months. |
| monthly_installment | DECIMAL(12,2)| No | Fixed monthly payment (French amortization). |
| initial_credit_score | INTEGER | No | Borrower score at time of underwriting. |
| initial_risk_grade | VARCHAR(5) | No | Internal credit risk rating (A, B, C, D). |

---

### Fact_Loan_Monthly_Snapshot (\ct_loan_monthly_snapshot\)
* **Grain:** One record per active/closed loan per month-end evaluation date.
* **Primary Key:** \snapshot_id\ (format SNP_{loan_id}_{YYYYMM}).
* **Foreign Keys:** \snapshot_date_id\, \loan_id\, \customer_id\, \product_id\.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| snapshot_id | VARCHAR(50) | No | Unique snapshot record key. |
| snapshot_date_id | INTEGER | No | Surrogate foreign key to dim_date. |
| snapshot_date | DATE | No | Month-end evaluation date. |
| loan_id | INTEGER | No | Foreign key to dim_loan. |
| customer_id | INTEGER | No | Foreign key to dim_customer. |
| product_id | INTEGER | No | Foreign key to dim_product. |
| months_on_books | INTEGER | No | Elapsed months since origination (MOB). |
| outstanding_principal | DECIMAL(14,2)| No | Remaining unpaid principal balance. |
| accrued_interest | DECIMAL(12,2)| No | Monthly interest portion accrued. |
| days_past_due | INTEGER | No | Days past due (DPD) on evaluation date. |
| delinquency_bucket | VARCHAR(20) | No | Aging bucket (Current, 1-30, 31-60, 61-90, 90+). |
| is_par30 | BOOLEAN | No | True if DPD > 30 days. |
| is_par60 | BOOLEAN | No | True if DPD > 60 days. |
| is_par90 | BOOLEAN | No | True if DPD > 90 days. |
| is_npl | BOOLEAN | No | True if loan is non-performing (DPD >= 90). |
| loan_status | VARCHAR(20) | No | Portfolio status (Performing, Delinquent, NPL, Paid). |

---

### Fact_Daily_Repayment (\ct_daily_repayment\)
* **Grain:** One record per transaction collection event.
* **Primary Key:** \epayment_id\ (format REP_{loan_id}_{mob}).
* **Foreign Keys:** \payment_date_id\, \loan_id\.

| Column Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| repayment_id | VARCHAR(50) | No | Unique payment event identifier. |
| payment_date_id | INTEGER | No | Surrogate foreign key to dim_date. |
| payment_date | DATE | No | Transaction posting date. |
| loan_id | INTEGER | No | Foreign key to dim_loan. |
| principal_paid | DECIMAL(12,2)| No | Portion of payment allocated to principal reduction. |
| interest_paid | DECIMAL(12,2)| No | Portion of payment allocated to interest income. |
| fees_paid | DECIMAL(12,2)| No | Late fees or penalty charges collected. |
| total_paid | DECIMAL(12,2)| No | Total collected payment (principal + interest + fees). |
| days_past_due_at_payment | INTEGER | No | Delinquency level at payment execution. |