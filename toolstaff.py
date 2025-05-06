def main():
    print("=== Ferramenta da STAFF ===")
    print("1. Ver Logs")
    print("2. Checar status")
    print("3. Sair")

    opcao = input("Escolha uma opção: ")
    if opcao == "1":
        print("Exibindo logs...")
    elif opcao == "2":
        print("Tudo funcionando normalmente.")
    elif opcao == "3":
        print("Saindo...")
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
