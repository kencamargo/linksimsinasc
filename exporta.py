import os.path
import duckdb

def export():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
        
    checkfile = os.path.isfile('./'+dbfile)    
    
    if not checkfile:
        print("Arquivo inexistente")
        return
    
    conn = duckdb.connect(dbfile)
    #conn.execute("SET THREADS TO 4;")
    #tabelas: pairs, pairscores, best_pairs
    
    choices = {'1':'pairs','2':'pairscores','3':'best_pairs'}
    print("Escolha a tabela-chave para exportacao:")
    print("[1] Tabela de pares gerados no linkage")
    print("[2] Tabela de pares com escores adicionais")
    print("[3] Tabela de pares otimizados")
    choice = input("Sua opcao (1): ")
    if choice not in choices:
        choice = "1"
        
    exportfile = input(f"Nome do arquivo exportado (combinado_{choices[choice]}.csv): ")
    if not exportfile:
        exportfile = f"combinado_{choices[choice]}.csv"    
    
    conn.execute(
    f'''
    copy (
    select t1.*,
    columns(t2.* EXCLUDE (UNIQUE_ID)) as 'SIM_\\0', 
    columns(t3.* EXCLUDE (UNIQUE_ID)) as 'SINASC_\\0' 
    from {choices[choice]} as t1 
        left join sim as t2 on t2.UNIQUE_ID = t1.SIMUID 
        left join sinasc as t3 on t3.UNIQUE_ID = t1.SINASCUID
    ) to '{exportfile}' (header, delimiter ',');
    '''
    )
    conn.close()
    print("Exportacao completa.")
    return
    
def main():
    export()
    

if __name__ == "__main__":
    main()
