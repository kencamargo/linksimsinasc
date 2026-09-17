import os.path
import duckdb

def runcalc():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
        
    checkfile = os.path.isfile('./'+dbfile)    
    
    if not checkfile:
        print("Arquivo inexistente")
        return
        
    print("Entre valores com ponto para decimais.")
    vmax = input("Valor maximo: ")
    if not vmax:
        vmax = "49.92"
    vmin = input("Valor minimo: ")    
    if not vmin:
        vmin = "0"    
    conn = duckdb.connect(dbfile)
    conn.execute("DROP TABLE IF EXISTS pairscores;")
    conn.execute(
    """
    CREATE TABLE pairscores (
            SIMUID UUID,
            SINASCUID UUID,
            CNASC FLOAT,
            CIDADE FLOAT,
            CGRAV FLOAT,
            CPARTO FLOAT,
            CPESO FLOAT,
            CTOTAL FLOAT,
            CRACACOR INTEGER,
            CESCMAE INTEGER, 
            CQTDFILVIVO INTEGER,
            CQTDFILMORT INTEGER, 
            CGESTACAO INTEGER,
            CSEMAGESTAC INTEGER,
            CTOTAL2 INTEGER,
        );
    """
    )
    conn.execute(
    f"""
    INSERT INTO pairscores
SELECT
    t1.*,
    CASE 
        WHEN t2.RACACOR IS NULL or t3.RACACOR IS NULL THEN 0
        WHEN t2.RACACOR = t3.RACACOR THEN 1
        ELSE -1
    END AS CRACACOR,    
    CASE 
        WHEN t2.ESCMAE IS NULL or t3.ESCMAE IS NULL THEN 0
        WHEN t2.ESCMAE = t3.RACACOR THEN 1
        ELSE -1
    END AS CESCMAE,
    CASE 
        WHEN t2.QTDFILVIVO IS NULL or t3.QTDFILVIVO IS NULL THEN 0
        WHEN t2.QTDFILVIVO = t3.QTDFILVIVO THEN 1
        ELSE -1
    END AS CQTDFILVIVO, 
    CASE 
        WHEN t2.QTDFILMORT IS NULL or t3.QTDFILMORT IS NULL THEN 0
        WHEN t2.QTDFILMORT = t3.QTDFILMORT THEN 1
        ELSE -1
    END AS CQTDFILMORT, 
    CASE 
        WHEN t2.GESTACAO IS NULL or t3.GESTACAO IS NULL THEN 0
        WHEN t2.GESTACAO = t3.GESTACAO THEN 1
        ELSE -1
    END AS CGESTACAO,
    CASE 
        WHEN t2.SEMAGESTAC IS NULL or t3.SEMAGESTAC IS NULL THEN 0
        WHEN t2.SEMAGESTAC = t3.SEMAGESTAC THEN 1
        ELSE -1
    END AS CSEMAGESTAC,
    CRACACOR + CESCMAE+ CQTDFILVIVO + CQTDFILMORT + CGESTACAO + CSEMAGESTAC AS CTOTAL2
    FROM pairs AS t1
        LEFT JOIN sim AS t2 ON t2.UNIQUE_ID = t1.SIMUID 
        LEFT JOIN sinasc AS t3 ON t3.UNIQUE_ID = t1.SINASCUID
    WHERE t1.CTOTAL < {float(vmax)} AND t1.CTOTAL > {float(vmin)};
    """
    )
    conn.close()
    print("Operacao completa.")
    return
    
def main():
    runcalc()    

if __name__ == "__main__":
    main()
