import duckdb
import sys

con = duckdb.connect()

# 1. Ejecutar DDL
with open('sql/01_schema_ddl.sql', 'r', encoding='utf-8') as f:
    ddl = f.read()
con.execute(ddl)

# 2. Cargar datos desde CSV
con.execute("INSERT INTO dim_customer SELECT * FROM read_csv_auto('data/dim_customer.csv');")
con.execute("INSERT INTO dim_product SELECT * FROM read_csv_auto('data/dim_product.csv');")
con.execute("INSERT INTO dim_date SELECT * FROM read_csv_auto('data/dim_date.csv');")
con.execute("INSERT INTO dim_loan SELECT * FROM read_csv_auto('data/dim_loan.csv');")
con.execute("INSERT INTO fct_loan_monthly_snapshot SELECT * FROM read_csv_auto('data/fct_loan_monthly_snapshot.csv');")
con.execute("INSERT INTO fct_daily_repayment SELECT * FROM read_csv_auto('data/fct_daily_repayment.csv');")

print("Datos cargados correctamente en memoria DuckDB.")

# 3. Ejecutar pruebas de calidad
with open('sql/02_data_quality_tests.sql', 'r', encoding='utf-8') as f:
    tests_query = f.read()

failures = con.execute(tests_query).fetchall()

if len(failures) == 0:
    print("SUCCESS: Todas las pruebas de calidad de datos pasaron con 0 anomalías (0 failed records).")
    sys.exit(0)
else:
    print(f"FAILED: Se encontraron {len(failures)} pruebas fallidas:")
    for row in failures:
        print(f" - {row[0]}: {row[1]} registros con error")
    sys.exit(1)