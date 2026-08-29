import os.path
import duckdb

def main():
    dbfile = input("Nome da base de dados (projeto.duckdb):")
    if not dbfile:
        dbfile = "projeto.duckdb"
    conn = duckdb.connect(dbfile)
    exportfile = input("Nome do arquivo exportado (combinado.csv):")
    if not exportfile:
        exportfile = "combinado.csv"
    conn.execute("SET THREADS TO 4;")
    conn.execute(
    f'''
    copy (
    select t1.*,
    columns(t2.*) as 'SIM_\\0', 
    columns(t3.*) as 'SINASC_\\0' 
    from pairs as t1 
        left join sim as t2 on t2.UNIQUE_ID = t1.SIMUID 
        left join sinasc as t3 on t3.UNIQUE_ID = t1.SINASCUID
    ) to '{exportfile}' (header, delimiter ',');
    '''
    )
    conn.close()
    print("Exportacao completa.")

if __name__ == "__main__":
    main()
