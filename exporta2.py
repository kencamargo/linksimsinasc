import os.path
import duckdb

def main():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
    conn = duckdb.connect(dbfile)
    exportfile = input("Nome do arquivo exportado (combinado2.csv): ")
    if not exportfile:
        exportfile = "combinado2.csv"
    #conn.execute("SET THREADS TO 4;")
    conn.execute(
    f'''
    copy (
    select t1.*,
    columns(t2.* EXCLUDE (UNIQUE_ID)) as 'SIM_\\0', 
    columns(t3.* EXCLUDE (UNIQUE_ID)) as 'SINASC_\\0' 
    from pairscores as t1 
        left join sim as t2 on t2.UNIQUE_ID = t1.SIMUID 
        left join sinasc as t3 on t3.UNIQUE_ID = t1.SINASCUID
    ) to '{exportfile}' (header, delimiter ',');
    '''
    )
    conn.close()
    print("Exportacao completa.")

if __name__ == "__main__":
    main()
