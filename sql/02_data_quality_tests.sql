-- ============================================================================
-- DATA QUALITY & GOVERNANCE SUITE: CREDIT RISK PORTFOLIO
-- Target: DuckDB / PostgreSQL
-- ============================================================================

-- Test 1: Unicidad de claves primarias en dimensiones
SELECT 'dim_customer_pk_duplicates' AS test_name, COUNT(*) - COUNT(DISTINCT customer_id) AS failed_records
FROM dim_customer
HAVING failed_records > 0

UNION ALL

SELECT 'dim_loan_pk_duplicates' AS test_name, COUNT(*) - COUNT(DISTINCT loan_id) AS failed_records
FROM dim_loan
HAVING failed_records > 0

UNION ALL

-- Test 2: Integridad referencial de préstamos huérfanos
SELECT 'orphan_loans_without_customer' AS test_name, COUNT(*) AS failed_records
FROM dim_loan l
LEFT JOIN dim_customer c ON l.customer_id = c.customer_id
WHERE c.customer_id IS NULL
HAVING failed_records > 0

UNION ALL

-- Test 3: Validación de rangos crediticios (DPD >= 0 y Score 300-850)
SELECT 'invalid_credit_score_range' AS test_name, COUNT(*) AS failed_records
FROM dim_customer
WHERE credit_score < 300 OR credit_score > 850
HAVING failed_records > 0

UNION ALL

SELECT 'negative_dpd_records' AS test_name, COUNT(*) AS failed_records
FROM fct_loan_monthly_snapshot
WHERE days_past_due < 0
HAVING failed_records > 0

UNION ALL

-- Test 4: Consistencia de capital pendiente (no negativo y <= principal original)
SELECT 'outstanding_exceeds_principal' AS test_name, COUNT(*) AS failed_records
FROM fct_loan_monthly_snapshot s
JOIN dim_loan l ON s.loan_id = l.loan_id
WHERE s.outstanding_principal < 0 OR s.outstanding_principal > (l.original_principal + 1.0)
HAVING failed_records > 0;