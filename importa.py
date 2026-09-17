import os.path
import duckdb

def checkfields(filename,fieldnames):
    complete = True    
    with open(filename, 'r') as file:
        headerline = file.readline()
        header = headerline[:-1].replace('"','').split(',')
        #print(header)
        for fld in fieldnames:
            if fld not in header:
                print(f'{filename} nao tem campo {fld}')
                complete = False
                break
    return complete


def main():
    simfile = input("Nome do arquivo SIM: ")    
    sinascfile = input("Nome do arquivo SINASC: ")
    dbfile = input("Nome da base de dados (projeto.duckdb): ")
    if not dbfile:
        dbfile = "projeto.duckdb"

    checkfiles = os.path.isfile('./'+simfile) and os.path.isfile('./'+sinascfile)

    if checkfiles:
        fieldnames = 'CODESTAB,DTNASC,SEXO,IDADEMAE,GRAVIDEZ,PARTO,PESO,CODMUNRES,RACACOR,ESCMAE,QTDFILVIVO,QTDFILMORT,GESTACAO,SEMAGESTAC,IDADEMAE'.split(',')
        test = checkfields(sinascfile, fieldnames)
        if not test:
            return
        fieldnames.append('LOCOCOR')
        fieldnames.append('CODMUNOCOR')    
        test = checkfields(simfile, fieldnames)
        if not test:
            return
        conn = duckdb.connect(dbfile)        
        #conn.execute("SET THREADS TO 4;")
        conn.execute("DROP TABLE IF EXISTS sim;")
        conn.execute("DROP TABLE IF EXISTS sinasc;")
        conn.execute(
        '''
        CREATE TABLE sim AS
        SELECT 
            uuid() AS UNIQUE_ID,
            ' ' AS FLAG,
            CASE 
                WHEN csim.CODMUNOCOR IS NULL OR TRIM(csim.CODMUNOCOR) = '' THEN 'NA'
                WHEN LENGTH(TRIM(csim.CODMUNOCOR)) < 2 THEN UPPER(TRIM(csim.CODMUNOCOR))
                ELSE LEFT(TRIM(csim.CODMUNOCOR), 2)
            END AS UF,   
            CASE 
                WHEN LENGTH(csim.DTNASC) = 8 THEN SUBSTRING(csim.DTNASC,3,2)
                ELSE NULL
            END AS MESNASC, 
            *            
        FROM read_csv(?, header=True, all_varchar=True) AS csim;
        ''', [simfile]
        )
        
        conn.execute(
        '''
        CREATE TABLE sinasc AS    
SELECT 
        uuid() AS UNIQUE_ID,
        CASE 
            WHEN csinasc.CODMUNNASC IS NULL OR TRIM(csinasc.CODMUNNASC) = '' THEN 'NA'
            WHEN LENGTH(TRIM(csinasc.CODMUNNASC)) < 2 THEN UPPER(TRIM(csinasc.CODMUNNASC))
            ELSE LEFT(TRIM(csinasc.CODMUNNASC), 2)
        END AS UF,        
        CASE 
            WHEN LENGTH(csinasc.DTNASC) = 8 THEN SUBSTRING(csinasc.DTNASC,3,2)
            ELSE NULL
        END AS MESNASC, 
        * RENAME (CODMUNNASC AS CODMUNOCOR)       
    FROM read_csv(?, header=True, all_varchar=True) AS csinasc;
        ''',[sinascfile]
        )
    
        conn.execute(
        '''
        UPDATE sim 
        SET LOCOCOR = CASE WHEN LOCOCOR IN ('9', 'NA', '') THEN NULL ELSE LOCOCOR END, 
            IDADEMAE = CASE WHEN IDADEMAE IN ('99', 'NA', '') THEN NULL ELSE IDADEMAE END,
            ESCMAE = CASE WHEN ESCMAE IN ('9', 'NA', '') THEN NULL ELSE ESCMAE END,
            QTDFILMORT = CASE WHEN QTDFILMORT IN ('99', 'NA', '') THEN NULL ELSE QTDFILMORT END,
            QTDFILVIVO = CASE WHEN QTDFILVIVO IN ('99', 'NA', '') THEN NULL ELSE QTDFILVIVO END,
            GRAVIDEZ = CASE WHEN GRAVIDEZ IN ('9', 'NA', '') THEN NULL ELSE GRAVIDEZ END,
            SEMAGESTAC = CASE WHEN SEMAGESTAC IN ('99', 'NA', '') THEN NULL ELSE SEMAGESTAC END,
            GESTACAO = CASE WHEN GESTACAO IN ('9', 'NA', '') THEN NULL ELSE GESTACAO END,
            PARTO = CASE WHEN PARTO IN ('9', 'NA', '') THEN NULL ELSE PARTO END,
            PESO = CASE WHEN PESO IN ('9', 'NA', '') THEN NULL ELSE PESO END,
            UF = CASE 
                WHEN CODMUNOCOR IN('2906105', '2907509', '2909901', '2917706', '2918407', '2924108', '2930204', '2930709', '2932002') THEN '26'
                WHEN CODMUNOCOR IN('3110506', '3127500', '3165005') THEN '35'
                WHEN UF = '52' THEN '53'
                WHEN CODMUNOCOR = '4102604' THEN '42'
                ELSE UF END
            WHERE
                LOCOCOR IN ('9', 'NA', '') OR 
                IDADEMAE IN ('99', 'NA', '') OR 
                ESCMAE IN ('9', 'NA', '') OR 
                QTDFILMORT IN ('99', 'NA', '') OR
                QTDFILVIVO IN ('99', 'NA', '') OR  
                GRAVIDEZ IN ('9', 'NA', '') OR 
                SEMAGESTAC IN ('99', 'NA', '') OR 
                GESTACAO IN ('9', 'NA', '') OR 
                PARTO IN ('9', 'NA', '') OR 
                PESO IN ('9', 'NA', '') OR
                CODMUNOCOR IN ('2906105', '2907509', '2909901', '2917706', '2918407', '2924108', '2930204', '2930709', '2932002', '3110506', '3127500', '3165005', '4102604') OR
                UF = '52';            
            '''
        )
        
        conn.execute(
        '''
        UPDATE sinasc
        SET LOCNASC = CASE WHEN LOCNASC IN ('9', 'NA', '') THEN NULL ELSE LOCNASC END,
            IDADEMAE = CASE WHEN IDADEMAE IN ('99', 'NA', '') THEN NULL ELSE IDADEMAE END,
            ESTCIVMAE = CASE WHEN ESTCIVMAE IN ('9', 'NA', '') THEN NULL ELSE ESTCIVMAE END,
            ESCMAE = CASE WHEN ESCMAE IN ('9', 'NA', '') THEN NULL ELSE ESCMAE END,
            QTDFILVIVO = CASE WHEN QTDFILVIVO IN ('99', 'NA', '') THEN NULL ELSE QTDFILVIVO END,
            QTDFILMORT = CASE WHEN QTDFILMORT IN ('99', 'NA', '') THEN NULL ELSE QTDFILMORT END,
            GESTACAO = CASE WHEN GESTACAO IN ('9', 'NA', '') THEN NULL ELSE GESTACAO END,
            GRAVIDEZ = CASE WHEN GRAVIDEZ IN ('9', 'NA', '') THEN NULL ELSE GRAVIDEZ END,
            PARTO = CASE WHEN PARTO IN ('9', 'NA', '') THEN NULL ELSE PARTO END,
            PESO = CASE WHEN PESO IN ('9', 'NA', '') THEN NULL ELSE PESO END,      
            UF = CASE 
                WHEN CODMUNOCOR IN('2906105', '2907509', '2909901', '2917706', '2918407', '2924108', '2930204', '2930709', '2932002') THEN '26'
                WHEN CODMUNOCOR IN('3110506', '3127500', '3165005') THEN '35'
                WHEN CODMUNOCOR = '4102604' THEN '42'
                WHEN UF = '52' THEN '53'
                ELSE UF END
            WHERE
                LOCNASC IN ('9', 'NA', '') OR 
                IDADEMAE IN ('99', 'NA', '') OR 
                ESTCIVMAE IN ('9', 'NA', '') OR 
                ESCMAE IN ('9', 'NA', '') OR 
                QTDFILMORT IN ('99', 'NA', '') OR 
                GRAVIDEZ IN ('9', 'NA', '') OR 
                GESTACAO IN ('9', 'NA', '') OR 
                PARTO IN ('9', 'NA', '') OR 
                PESO IN ('9', 'NA', '') OR
                CODMUNOCOR IN ('2906105', '2907509', '2909901', '2917706', '2918407', '2924108', '2930204', '2930709', '2932002', '3110506', '3127500', '3165005', '4102604') OR
                UF = '52';
        '''
        )
        
        conn.close()
        print("Importacao encerrada.")
    else:
        print("Um ou ambos arquivos inexistente(s).")
    

if __name__ == "__main__":
    main()
