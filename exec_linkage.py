import duckdb
import time
import math
from datetime import date, datetime

UNIQUE_ID = 0
CODESTAB = 1
DTNASC = 2
SEXO = 3
IDADEMAE = 4
GRAVIDEZ = 5
PARTO = 6
PESO = 7
CODMUNRES = 8
UF = 9
MESNASC = 10

LIM_MIN = 0.0

def todate(datestr: str) -> date:
    if datestr is None:
        return -1
    if len(datestr) < 8:
        datestr = '0' + datestr    
    try:
        yr = datestr[4:]
        mo = datestr[2:4]
        dy = datestr[:2]
        year = int(yr)
        month = int(mo)
        day = int(dy)        
        thedate = date(year,month,day)
    except Exception as error:
        return -1
    else:
        return thedate

def datediff(mindate: str, maxdate: str) -> int:
    day1 = todate(maxdate)
    day2 = todate(mindate)
    if day1 == -1 or day2 == -1:
        return -1
    delta = day1 - day2
    diffstr = str(delta).split(' ')[0]
    if diffstr == '0:00:00':
        diffstr = '0'
    return abs(int(diffstr))

def docompares(simrec, sinascrec):
    comparisons = [-10.38, -6.04, -1.84, -7.68, -7.19] # discordancia
    diffs = [0.0,0.0,0.0,0.0,0.0,0.0]

    if simrec[DTNASC] is None or sinascrec[DTNASC] is None:
        comparisons[0] = 0.0
        diffs[0] = float('nan')
    else:
        days = datediff(simrec[DTNASC], sinascrec[DTNASC]) 
        diffs[0] = days
        if days == -1:
            comparisons[0] = 0.0 
        elif days == 0:
            comparisons[0] = 19.52
        elif days <= 1:
            comparisons[0] = 9.56
        elif days <= 2:
            comparisons[0] = -0.41
            
    if simrec[IDADEMAE] is None or sinascrec[IDADEMAE] is None:
        comparisons[1] = 0.0
        diffs[1] = float('nan')
    else:
        anos = abs(int(simrec[IDADEMAE])-int(sinascrec[IDADEMAE])) 
        diffs[1] = anos
        if anos == 0:
            comparisons[1] = 11.69
        elif anos <= 1:
            comparisons[1] = 5.78
        elif anos <= 2:
            comparisons[1] = -0.13
    
    if simrec[GRAVIDEZ] is None or sinascrec[GRAVIDEZ] is None:
        comparisons[2] = 0.0
        diffs[2] = float('nan')
    elif simrec[GRAVIDEZ] == sinascrec[GRAVIDEZ]: 
        comparisons[2] = 0.1
        diffs[2] = 0.0
    else:
        diffs[2] = abs(int(simrec[GRAVIDEZ])-int(sinascrec[GRAVIDEZ])) 

        
    if simrec[PARTO] is None or sinascrec[PARTO] is None:
        comparisons[3] = 0.0   
        diffs[3] = float('nan')
    elif simrec[PARTO] == sinascrec[PARTO]: 
        comparisons[3] = 2.68 
        diffs[3] = 0.0
    else:
        diffs[3] = abs(int(simrec[PARTO])-int(sinascrec[PARTO])) 
        
    if simrec[PESO] is None or sinascrec[PESO] is None:
        comparisons[4] = 0.0
        diffs[4] = float('nan')
    else:
        peso = abs(int(simrec[PESO])-int(sinascrec[PESO])) 
        diffs[4] = peso
        if peso == 0:
            comparisons[4] = 15.93
        elif peso <= 100:
            comparisons[4] = 8.23
        elif peso <= 200:
            comparisons[4] = 0.52
            
    total = sum(comparisons)
    diffs[5] = total
                    
    return diffs


'''
def check_index(conn, index_name):
    query = "SELECT 1 FROM duckdb_indexes WHERE index_name = ?;"
    exists = conn.execute(query, [index_name]).fetchone()
    return not exists
'''    

def duckdb_linkage_wrapper(sim_row, sinasc_row):    
    sim_mapped = [
        sim_row.get('UNIQUE_ID'), sim_row.get('CODESTAB'), sim_row.get('DTNASC'),
        sim_row.get('SEXO'), sim_row.get('IDADEMAE'), sim_row.get('GRAVIDEZ'),
        sim_row.get('PARTO'), sim_row.get('PESO'), sim_row.get('CODMUNRES'),
        sim_row.get('UF'), sim_row.get('MESNASC')
    ]
    
    sinasc_mapped = [
        sinasc_row.get('UNIQUE_ID'), sinasc_row.get('CODESTAB'), sinasc_row.get('DTNASC'),
        sinasc_row.get('SEXO'), sinasc_row.get('IDADEMAE'), sinasc_row.get('GRAVIDEZ'),
        sinasc_row.get('PARTO'), sinasc_row.get('PESO'), sinasc_row.get('CODMUNRES'),
        sinasc_row.get('UF'), sinasc_row.get('MESNASC')
    ]
    
    test = docompares(sim_mapped, sinasc_mapped)
    #score_total = sum(test)
    
    return {
        'cnasc': float(test[0]),
        'cidade': float(test[1]),
        'cgrav': float(test[2]),
        'cparto': float(test[3]),
        'cpeso': float(test[4]),
        'ctotal': float(test[5])
    }

def runlinkage_parallel(conn, fnos, useflag=True):
    start_time = time.perf_counter()
    
    colunas_map = {
        CODESTAB: "CODESTAB", SEXO: "SEXO", CODMUNRES: "CODMUNRES",
        DTNASC: "DTNASC", UNIQUE_ID: "UNIQUE_ID", MESNASC: "MESNASC",
        UF: "UF" 
    }
    
    join_conditions = [f"sim.{colunas_map[fno]} = sinasc.{colunas_map[fno]}" for fno in fnos]
    join_clause = " AND ".join(join_conditions)
    
    flag_filter = "WHERE FLAG != '+'" if useflag else ""
    
    op = conn.execute(f"""
    SELECT COUNT(*) 
    FROM pairs;  
    """) 
    nrecs = op.fetchone()[0] 
    
    query_process = f"""
        INSERT INTO pairs
        WITH calculo AS (
            SELECT 
                sim.UNIQUE_ID as SIMUID,
                sinasc.UNIQUE_ID as SINASCUID,
                calcular_scores(sim, sinasc) as res_struct
            FROM (
                SELECT * FROM sim {flag_filter}
            ) sim
            INNER JOIN sinasc ON {join_clause}
        )
        SELECT 
            SIMUID,
            SINASCUID,
            res_struct.cnasc as CNASC,
            res_struct.cidade as CIDADE,
            res_struct.cgrav as CGRAV,
            res_struct.cparto as CPARTO,
            res_struct.cpeso as CPESO,
            round(res_struct.ctotal, 2) as CTOTAL
        FROM calculo
        WHERE res_struct.ctotal >= {LIM_MIN}    
        ON CONFLICT (SIMUID, SINASCUID) DO NOTHING;    
    """

    conn.execute(query_process)
    
    link_time = time.perf_counter()
    elapsed_time = link_time - start_time
    print(f"Tempo transcorrido no link: {int(elapsed_time)} segundos.")
        
    op = conn.execute(f"""
    SELECT COUNT(*) 
    FROM pairs;  
    """) 
    nrecs = op.fetchone()[0] - nrecs    
        
    print("Atualizando campo FLAG na tabela SIM...")
    
    CTOTALMAX = 49.92
    query_update = f"""
        UPDATE sim 
        SET FLAG = '+' 
        WHERE UNIQUE_ID IN (
            SELECT SIMUID 
            FROM pairs 
            WHERE CTOTAL >= {CTOTALMAX}
        ) AND FLAG <> '+';
    """
    cursor = conn.execute(query_update)
    markregs = cursor.fetchone()[0]
    
    print(f"Registros marcados: {markregs}\nPares acrescentados: {nrecs}")
    
    end_time = time.perf_counter()
    update_time = end_time - link_time
    elapsed_time = end_time - start_time
    if int(update_time) > 0:
        print(f"Tempo transcorrido na atualizacao: {int(update_time)} segundos\nTempo total transcorrido no passo: {int(elapsed_time)} segundos.")
    return markregs

def runlink():
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"
    conn = duckdb.connect(dbfile)
    
    valmin = input("Limiar minimo (0.0): ")
    if valmin:
        LIM_MIN = float(valmin)
    
    threads = input("Numero de processos: ")
    if threads and int(threads) > 0:
    	conn.execute(f"SET THREADS TO {threads};")
    
    start_time = time.perf_counter()
    
    print(f"Iniciando processamento em {datetime.now()}")
    
    print("Inicializando...")
    
    conn.execute('DROP INDEX IF EXISTS firstblock;')
    conn.execute("CREATE INDEX firstblock ON sinasc(CODESTAB, SEXO, CODMUNRES, MESNASC);")
        
    conn.execute('DROP INDEX IF EXISTS secondblock;')
    conn.execute("CREATE INDEX secondblock ON sinasc(CODESTAB, SEXO, CODMUNRES);")
    
    conn.execute('DROP INDEX IF EXISTS thirdblock;')
    conn.execute("CREATE INDEX thirdblock ON sinasc(CODESTAB, SEXO, MESNASC);")    
    
    conn.execute('DROP INDEX IF EXISTS fourthblock;')
    conn.execute("CREATE INDEX fourthblock ON sinasc(CODESTAB, CODMUNRES, MESNASC);")
        
    conn.execute('DROP INDEX IF EXISTS fifthblock;')
    conn.execute("CREATE INDEX fifthblock ON sinasc(UF, SEXO, CODMUNRES, MESNASC);")
    
    #zera FLAG
    conn.execute(
    """
        UPDATE sim 
        SET FLAG = ' ' 
        WHERE FLAG = '+';
    """)
        
    conn.execute("DROP TABLE IF EXISTS pairs;")
    conn.execute(
    '''
        CREATE TABLE pairs (
            SIMUID UUID,
            SINASCUID UUID,
            CNASC FLOAT,
            CIDADE FLOAT,
            CGRAV FLOAT,
            CPARTO FLOAT,
            CPESO FLOAT,
            CTOTAL FLOAT,
            PRIMARY KEY (SIMUID, SINASCUID)
        );
    '''    
    )  
    
    return_type = "STRUCT(cnasc FLOAT, cidade FLOAT, cgrav FLOAT, cparto FLOAT, cpeso FLOAT, ctotal FLOAT)"
    conn.create_function("calcular_scores", duckdb_linkage_wrapper, return_type=return_type)  
    
    fnos = [CODESTAB, SEXO, CODMUNRES, MESNASC]
    
    print("Executando passo 1...")
    
    markregs = runlinkage_parallel(conn, fnos, useflag=False)
    
    fnos = [CODESTAB, CODMUNRES, MESNASC]
    
    print("Executando passo 2...")
    
    markregs += runlinkage_parallel(conn, fnos)
    
    fnos = [CODESTAB, SEXO, MESNASC]
    
    print("Executando passo 3...")
    
    markregs += runlinkage_parallel(conn, fnos)
    
    fnos = [CODESTAB, SEXO, CODMUNRES]
    
    print("Executando passo 4...")
    
    markregs += runlinkage_parallel(conn, fnos)
    
    fnos = [UF, SEXO, CODMUNRES, MESNASC]
    
    print("Executando passo 5...")
    
    markregs += runlinkage_parallel(conn, fnos)
    
    op = conn.execute(f"""
    SELECT COUNT(*) 
    FROM pairs;  
    """) 
    nrecs = op.fetchone()[0]
        
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Processamento completo.\nTempo total transcorrido: {int(elapsed_time)} segundos.\nTotal de registros marcados: {markregs}\nTotal de pares gerados: {nrecs}")
    
    conn.close()
    
    return
   
def main():
    runlink()   

if __name__ == "__main__":
    main()

