import os
import math
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

np.random.seed(42)
random.seed(42)

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Dim Date (2024-01-01 to 2026-12-31)
start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

dim_date = pd.DataFrame({
    'date_id': [int(d.strftime('%Y%m%d')) for d in date_range],
    'full_date': [d.strftime('%Y-%m-%d') for d in date_range],
    'year_num': [d.year for d in date_range],
    'quarter_num': [d.quarter for d in date_range],
    'month_num': [d.month for d in date_range],
    'month_name': [d.strftime('%B') for d in date_range],
    'year_month': [d.strftime('%Y-%m') for d in date_range],
    'is_month_end': [d.is_month_end for d in date_range]
})
dim_date.to_csv(os.path.join(DATA_DIR, 'dim_date.csv'), index=False)

# 2. Dim Product
products = [
    {'product_id': 1, 'product_name': 'Consumer Personal Loan', 'product_category': 'Unsecured', 'collateral_type': 'None', 'min_term_months': 12, 'max_term_months': 36, 'base_annual_rate': 0.1850},
    {'product_id': 2, 'product_name': 'Auto Financing', 'product_category': 'Secured', 'collateral_type': 'Vehicle', 'min_term_months': 24, 'max_term_months': 60, 'base_annual_rate': 0.1125},
    {'product_id': 3, 'product_name': 'Microbusiness Capital', 'product_category': 'Commercial', 'collateral_type': 'Commercial Asset', 'min_term_months': 6, 'max_term_months': 24, 'base_annual_rate': 0.2400},
    {'product_id': 4, 'product_name': 'Payroll Advance Loan', 'product_category': 'Unsecured', 'collateral_type': 'Salary', 'min_term_months': 6, 'max_term_months': 18, 'base_annual_rate': 0.1450}
]
dim_product = pd.DataFrame(products)
dim_product.to_csv(os.path.join(DATA_DIR, 'dim_product.csv'), index=False)

# 3. Dim Customer (N = 1,200)
n_customers = 1200
ages = np.clip(np.random.normal(loc=38, scale=10, size=n_customers).astype(int), 21, 68)
monthly_incomes = np.round(np.random.lognormal(mean=7.6, sigma=0.45, size=n_customers) * 1.5, 2)
raw_scores = np.clip(np.random.normal(loc=670, scale=80, size=n_customers).astype(int), 320, 840)

regions = ['North America', 'EMEA', 'LATAM Commercial', 'Asia-Pacific']
emp_types = ['Full-Time Corporate', 'Self-Employed Professional', 'Public Sector', 'Contractor']

customer_records = []
for i in range(n_customers):
    cid = 10001 + i
    score = raw_scores[i]
    if score >= 750:
        band = 'Excellent (750+)'
    elif score >= 680:
        band = 'Good (680-749)'
    elif score >= 600:
        band = 'Fair (600-679)'
    else:
        band = 'Subprime (<600)'
    
    customer_records.append({
        'customer_id': cid,
        'customer_name': f'Borrower_{cid}',
        'age': int(ages[i]),
        'monthly_income': float(monthly_incomes[i]),
        'credit_score': int(score),
        'credit_score_band': band,
        'employment_type': random.choice(emp_types),
        'region': random.choice(regions)
    })
dim_customer = pd.DataFrame(customer_records)
dim_customer.to_csv(os.path.join(DATA_DIR, 'dim_customer.csv'), index=False)

# 4. Dim Loan (N = 1,500 loans originated between 2024-01-01 and 2025-12-31)
n_loans = 1500
orig_dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='D')
loan_records = []

for i in range(n_loans):
    lid = 50001 + i
    cust = dim_customer.sample(1).iloc[0]
    prod = dim_product.sample(1).iloc[0]
    
    orig_date = random.choice(orig_dates)
    term = random.choice([12, 24, 36, 48])
    
    # Risk adjustment to interest rate
    score = cust['credit_score']
    if score >= 750:
        risk_grade = 'A'
        rate_adj = -0.02
    elif score >= 680:
        risk_grade = 'B'
        rate_adj = 0.00
    elif score >= 600:
        risk_grade = 'C'
        rate_adj = 0.035
    else:
        risk_grade = 'D'
        rate_adj = 0.075
        
    annual_rate = round(float(prod['base_annual_rate'] + rate_adj), 4)
    monthly_rate = annual_rate / 12.0
    
    if prod['product_id'] == 1:
        principal = round(random.uniform(2000, 15000), 2)
    elif prod['product_id'] == 2:
        principal = round(random.uniform(12000, 35000), 2)
    elif prod['product_id'] == 3:
        principal = round(random.uniform(5000, 25000), 2)
    else:
        principal = round(random.uniform(1000, 8000), 2)
        
    # French Amortization Formula
    installment = principal * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
    
    loan_records.append({
        'loan_id': lid,
        'customer_id': int(cust['customer_id']),
        'product_id': int(prod['product_id']),
        'origination_date': orig_date.strftime('%Y-%m-%d'),
        'origination_year_month': orig_date.strftime('%Y-%m'),
        'original_principal': float(principal),
        'annual_interest_rate': float(annual_rate),
        'term_months': int(term),
        'monthly_installment': round(float(installment), 2),
        'initial_credit_score': int(score),
        'initial_risk_grade': risk_grade
    })

dim_loan = pd.DataFrame(loan_records)
dim_loan.to_csv(os.path.join(DATA_DIR, 'dim_loan.csv'), index=False)

# 5. Monthly Snapshots & Repayments Generation
snapshot_records = []
repayment_records = []

# Monthly evaluation calendar: end of each month from 2024-01-31 to 2026-08-31
eval_dates = pd.date_range(start='2024-01-31', end='2026-08-31', freq='ME')

for _, loan in dim_loan.iterrows():
    lid = loan['loan_id']
    cid = loan['customer_id']
    pid = loan['product_id']
    orig_dt = pd.to_datetime(loan['origination_date'])
    term = loan['term_months']
    principal = loan['original_principal']
    r = loan['annual_interest_rate'] / 12.0
    pmt = loan['monthly_installment']
    risk = loan['initial_risk_grade']
    
    rem_principal = principal
    status = 'Current'
    consecutive_defaults = 0
    
    for mob, eval_dt in enumerate(eval_dates):
        if eval_dt < orig_dt:
            continue
            
        mob_count = int((eval_dt.year - orig_dt.year) * 12 + (eval_dt.month - orig_dt.month))
        if mob_count < 1 or mob_count > term + 6:
            continue
            
        # Probability of default transition based on risk grade
        p_miss = 0.015 if risk == 'A' else (0.035 if risk == 'B' else (0.075 if risk == 'C' else 0.14))
        is_missed = random.random() < p_miss
        
        if is_missed:
            consecutive_defaults += 1
        else:
            if consecutive_defaults > 0 and random.random() < 0.65:
                consecutive_defaults = max(0, consecutive_defaults - 1)
            elif consecutive_defaults == 0:
                consecutive_defaults = 0
                
        dpd = consecutive_defaults * 30
        
        if dpd == 0:
            bucket = 'Current (0 DPD)'
            status = 'Performing'
        elif dpd <= 30:
            bucket = '1-30 Days'
            status = 'Delinquent'
        elif dpd <= 60:
            bucket = '31-60 Days'
            status = 'Late'
        elif dpd <= 90:
            bucket = '61-90 Days'
            status = 'Default Alert'
        else:
            bucket = '90+ Days'
            status = 'Non-Performing (NPL)'
            
        # Repayment logic if paying
        if consecutive_defaults == 0 and rem_principal > 0:
            interest_part = rem_principal * r
            principal_part = min(rem_principal, pmt - interest_part)
            rem_principal = max(0.0, rem_principal - principal_part)
            
            repay_dt = eval_dt - timedelta(days=random.randint(1, 5))
            repayment_records.append({
                'repayment_id': f'REP_{lid}_{mob_count}',
                'payment_date_id': int(repay_dt.strftime('%Y%m%d')),
                'payment_date': repay_dt.strftime('%Y-%m-%d'),
                'loan_id': lid,
                'principal_paid': round(float(principal_part), 2),
                'interest_paid': round(float(interest_part), 2),
                'fees_paid': 0.0,
                'total_paid': round(float(principal_part + interest_part), 2),
                'days_past_due_at_payment': 0
            })
            
        if rem_principal == 0.0:
            status = 'Closed / Paid'
            bucket = 'Paid Off'
            dpd = 0
            
        snapshot_records.append({
            'snapshot_id': f'SNP_{lid}_{eval_dt.strftime("%Y%m")}',
            'snapshot_date_id': int(eval_dt.strftime('%Y%m%d')),
            'snapshot_date': eval_dt.strftime('%Y-%m-%d'),
            'loan_id': lid,
            'customer_id': cid,
            'product_id': pid,
            'months_on_books': mob_count,
            'outstanding_principal': round(float(rem_principal), 2),
            'accrued_interest': round(float(rem_principal * r), 2) if rem_principal > 0 else 0.0,
            'days_past_due': int(dpd),
            'delinquency_bucket': bucket,
            'is_par30': bool(dpd > 30),
            'is_par60': bool(dpd > 60),
            'is_par90': bool(dpd > 90),
            'is_npl': bool(dpd >= 90),
            'loan_status': status
        })
        
        if status == 'Closed / Paid':
            break

fct_snapshot = pd.DataFrame(snapshot_records)
fct_snapshot.to_csv(os.path.join(DATA_DIR, 'fct_loan_monthly_snapshot.csv'), index=False)

fct_repayment = pd.DataFrame(repayment_records)
fct_repayment.to_csv(os.path.join(DATA_DIR, 'fct_daily_repayment.csv'), index=False)

print(f'Generación completa en carpeta data/:')
print(f' - dim_date: {len(dim_date)} filas')
print(f' - dim_product: {len(dim_product)} filas')
print(f' - dim_customer: {len(dim_customer)} filas')
print(f' - dim_loan: {len(dim_loan)} filas')
print(f' - fct_loan_monthly_snapshot: {len(fct_snapshot)} filas')
print(f' - fct_daily_repayment: {len(fct_repayment)} filas')