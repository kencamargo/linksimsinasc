import calc_score, exec_linkage, exporta, importa, otimizasql

def main():
    keepon = True
    while keepon:    
        print("Opcoes disponiveis:")
        print("[1] Importa arquivos")
        print("[2] Executa linkage")
        print("[3] Calcula escores adicionais")
        print("[4] Otimiza tabela")
        print("[5] Exporta tabela(s)")
        print("[0] Encerra")
        choice = input("Escolha uma opcao (0): ")
        choices = {"1":importa.runimport,"2":exec_linkage.runlink,"3":calc_score.runcalc,"4":otimizasql.optimize,"5":exporta.export}
        if choice not in choices:
            keepon = False
        else:
            choices[choice]() 
    print("Encerrando.")           
    return 


if __name__ == "__main__":
    main()

