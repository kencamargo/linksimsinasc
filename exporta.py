import os.path
import duckdb

def exporttable(conn, table):
    exportfile = input(f"Nome do arquivo exportado ({table}_exportada.csv): ")
    if not exportfile:
        exportfile = f"{table}_exportada.csv"
    conn.execute(
    f'''
    copy (
    select *
    from {table} 
    ) to '{exportfile}' (header, delimiter ',');
    '''
    )

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
    
    choices = {'1':'*','2':'pairs','3':'best_pairs','4':'pairscores'}
    print("Escolha a(s) tabela(s) para exportacao:")
    print("[1] Tabelas originais com identificadores")
    print("[2] Tabela de pares gerados no linkage")
    print("[3] Tabela de pares otimizados")
    print("[4] Tabela de pares com escores adicionais")    
    print("[0] Retorna sem exportar")
    choice = input("Sua opcao (1): ")
    if choice not in choices:
        choice = "1"
        
    if choice == '1':    
        exporttable(conn, 'sim')
        exporttable(conn, 'sinasc')
    else:
        exporttable(conn, choices[choice])    
        
    conn.close()
    print("Exportacao completa.")
    return
    
def main():
    export()
    

if __name__ == "__main__":
    main()
