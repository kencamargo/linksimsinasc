import duckdb

def main():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
    conn = duckdb.connect(dbfile)
    op = conn.execute(
    """
    SELECT 
        COUNT(*) as total_pairs,
        MIN(CTOTAL) as min_CTOTAL,
        MAX(CTOTAL) as max_CTOTAL,
        AVG(CTOTAL) as avg_CTOTAL,
        -- Percentiles (ordered from lowest to highest)
        QUANTILE_CONT(CTOTAL, 0.25) as p25_CTOTAL,
        QUANTILE_CONT(CTOTAL, 0.50) as median_CTOTAL,
        QUANTILE_CONT(CTOTAL, 0.75) as p75_CTOTAL,
        QUANTILE_CONT(CTOTAL, 0.90) as p90_CTOTAL, -- Top 10% boundary
        QUANTILE_CONT(CTOTAL, 0.92) as p92_CTOTAL, -- Top 8% boundary (approx. 20k rows)
        QUANTILE_CONT(CTOTAL, 0.95) as p95_CTOTAL,
    -- Top 5% boundary
        QUANTILE_CONT(CTOTAL, 0.99) as p99_CTOTAL  -- Top 1% boundary
    FROM pairs;
    """)   
    result = op.fetchone()
    print(f"Total: {result[0]}")
    print(f"Min:   {result[1]:.2f}")
    print(f"Max:   {result[2]:.2f}")
    print(f"Media: {result[3]:.2f}")
    print(f"p25:   {result[4]:.2f}")
    print(f"p50:   {result[5]:.2f}")
    print(f"p75:   {result[6]:.2f}")
    print(f"p90:   {result[7]:.2f}")
    print(f"p92:   {result[8]:.2f}")
    print(f"p95:   {result[9]:.2f}")
    print(f"p99:   {result[10]:.2f}")
    
    vmin = input("Valor minimo (0.0): ")
    vmax = input("Valor maximo (49.92): ")
    if not vmin:
        vmin = "0.0"
    if not vmax:
        vmax = "49.92"
        
    op = conn.execute(f"""
    SELECT COUNT(*) 
    FROM pairs
    WHERE CTOTAL BETWEEN {float(vmin)} AND {float(vmax)};  
    """) 
    nrecs = op.fetchone()
    print(f"Total para processamento: {nrecs[0]}")
        
    conn.execute(f"""    
    CREATE OR REPLACE TABLE best_pairs AS
	WITH ranked_pairs AS (
		SELECT 
			SIMUID, 
			SINASCUID, 
			CTOTAL,			
			DENSE_RANK() OVER (PARTITION BY SIMUID ORDER BY CTOTAL DESC) as row_rank_sim,
			DENSE_RANK() OVER (PARTITION BY SINASCUID ORDER BY CTOTAL DESC) as row_rank_sinasc
		FROM pairs
		WHERE CTOTAL BETWEEN {float(vmin)} AND {float(vmax)}
		)
	SELECT SIMUID, SINASCUID, CTOTAL
	FROM ranked_pairs
	WHERE row_rank_sim = 1 AND row_rank_sinasc = 1;
    """)
    
    op = conn.execute(f"""
    SELECT COUNT(*) 
    FROM best_pairs;  
    """) 
    nrecs = op.fetchone() 
    
    op = conn.execute(f"""
    INSERT INTO best_pairs
    SELECT SIMUID, SINASCUID, CTOTAL 
    FROM pairs
    WHERE CTOTAL >= {float(vmax)};
    """)
    
    conn.close()
    print(f"Operacao completa.\nTotal processado: {nrecs[0]}")

if __name__ == "__main__":
    main()    
