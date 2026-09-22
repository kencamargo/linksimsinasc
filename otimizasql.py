import os.path
import duckdb

def optimize():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
    
    checkfile = os.path.isfile('./'+dbfile)    
    
    if not checkfile:
        print("Arquivo inexistente")
        return    
        
    conn = duckdb.connect(dbfile)
    op = conn.execute("""
    SELECT COUNT(*) 
    FROM pairs;
    """) 
    nrecs = op.fetchone()
    print(f"Total para processamento: {nrecs[0]}")
    
    conn.execute("DROP TABLE IF EXISTS best_pairs;")
            
    conn.execute("""    
    CREATE OR REPLACE TABLE best_pairs AS
	WITH ranked_pairs AS (
		SELECT 			
			*,				
			DENSE_RANK() OVER (PARTITION BY SIMUID ORDER BY CTOTAL DESC) as row_rank_sim,
			DENSE_RANK() OVER (PARTITION BY SINASCUID ORDER BY CTOTAL DESC) as row_rank_sinasc
		FROM pairs
		)
	SELECT * EXCLUDE (row_rank_sim, row_rank_sinasc)
	FROM ranked_pairs
	WHERE row_rank_sim = 1 AND row_rank_sinasc = 1;
    """)
    
    op = conn.execute("""
    SELECT COUNT(*) 
    FROM best_pairs;  
    """) 
    nrecs = op.fetchone()     
    
    conn.close()
    print(f"Operacao completa.\nTotal processado: {nrecs[0]}")
    return

def main():
    optimize()
if __name__ == "__main__":
    main()    
