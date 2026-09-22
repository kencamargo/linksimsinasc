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
            CCODESTAB INTEGER, 
            CSEXO INTEGER, 
            CCODMUNRES INTEGER, 
            CMESNASC INTEGER, 
            CUF INTEGER
        );
    """
    )
    conn.execute(
    """
    INSERT INTO pairscores
    SELECT
        t1.*,
        CASE 
            WHEN t2.RACACOR IS NULL or t3.RACACOR IS NULL THEN NULL
            WHEN t2.RACACOR = t3.RACACOR THEN 1
            ELSE 0
        END 
        AS CRACACOR,    
        CASE 
            WHEN t2.ESCMAE IS NULL or t3.ESCMAE IS NULL THEN NULL
            WHEN t2.ESCMAE = t3.RACACOR THEN 1
            ELSE 0
        END 
        AS CESCMAE,
        CASE 
            WHEN t2.QTDFILVIVO IS NULL or t3.QTDFILVIVO IS NULL THEN NULL
            WHEN t2.QTDFILVIVO = t3.QTDFILVIVO THEN 1
            ELSE 0
        END 
        AS CQTDFILVIVO, 
        CASE 
            WHEN t2.QTDFILMORT IS NULL or t3.QTDFILMORT IS NULL THEN NULL
            WHEN t2.QTDFILMORT = t3.QTDFILMORT THEN 1
            ELSE 0
        END 
        AS CQTDFILMORT, 
        CASE 
            WHEN t2.GESTACAO IS NULL or t3.GESTACAO IS NULL THEN NULL
            WHEN t2.GESTACAO = t3.GESTACAO THEN 1
            ELSE 0
        END 
        AS CGESTACAO,
        CASE 
            WHEN t2.SEMAGESTAC IS NULL or t3.SEMAGESTAC IS NULL THEN NULL
            WHEN t2.SEMAGESTAC = t3.SEMAGESTAC THEN 1
            ELSE 0
        END 
        AS CSEMAGESTAC,
        CASE 
            WHEN t2.CODESTAB IS NULL or t3.CODESTAB IS NULL THEN NULL
            WHEN t2.CODESTAB = t3.CODESTAB THEN 1
            ELSE 0
        END
        AS CCODESTAB, 
        CASE 
            WHEN t2.SEXO IS NULL or t3.SEXO IS NULL THEN NULL
            WHEN t2.SEXO = t3.SEXO THEN 1
            ELSE 0
        END
        AS CSEXO, 
        CASE 
            WHEN t2.CODMUNRES IS NULL or t3.CODMUNRES IS NULL THEN NULL
            WHEN t2.CODMUNRES = t3.CODMUNRES THEN 1
            ELSE 0
        END
        AS CCODMUNRES, 
        CASE 
            WHEN t2.MESNASC IS NULL or t3.MESNASC IS NULL THEN NULL
            WHEN t2.MESNASC = t3.MESNASC THEN 1
            ELSE 0
        END
        AS CMESNASC, 
        CASE 
            WHEN t2.UF IS NULL or t3.UF IS NULL THEN NULL
            WHEN t2.UF = t3.UF THEN 1
            ELSE 0
        END
        AS CUF
        FROM best_pairs AS t1
        LEFT JOIN sim AS t2 ON t2.UNIQUE_ID = t1.SIMUID 
        LEFT JOIN sinasc AS t3 ON t3.UNIQUE_ID = t1.SINASCUID;
    """
    )
    conn.close()
    print("Operacao completa.")
    return
    
def main():
    runcalc()    

if __name__ == "__main__":
    main()
