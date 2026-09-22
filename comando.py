import calc_score, exec_linkage, exporta, importa, otimizasql

def main():
    keepon = True
    while keepon:    
        print("Opcoes disponiveis:")
        print("[1] Importa arquivos")
        print("[2] Executa linkage")
        print("[3] Otimiza tabela")
        print("[4] Calcula escores adicionais")        
        print("[5] Exporta tabela(s)")
        print("[0] Encerra")
        choice = input("Escolha uma opcao (0): ")
        choices = {"1":importa.runimport,"2":exec_linkage.runlink,"3":otimizasql.optimize,"4":calc_score.runcalc,"5":exporta.export}
        if not choice or choice == '0':
            keepon = False
        elif choice in choices:
            choices[choice]() 
        else:
            print('Opcao invalida.')
    print("Encerrando.")           
    return 


if __name__ == "__main__":
    main()

