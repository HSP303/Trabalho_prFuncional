import os
import time

categorias = ['Contas', 'Superficial']
meta = 10000
saldo = 0

def imprimirMenu():
    #os.system('clear')
    print("""
=== MENU ===
1 - Entrada
2 - Saída
3 - Cadastrar Meta
4 - Cadastrar Categoria    
5 - Sair do Tédio (Precisa ter o telnet instalado e no PATH)
0 - Sair
    """)

def validaNum(valor, floatInt):
    valido = True
    msg = ''

    try:
        if floatInt == 1:
            valor = float(valor)
        else:
            valor = int(valor)
    except:
        valido = False
        msg = 'O valor não é um número. Digite um valor válido!'
        return (valido, msg)
    
    if(valor <= 0):
        valido = False
        msg = 'Digite uma valor maior que zero!'

    return (valido, msg)


def entrada(saldo):
    eValido = False
    while eValido == False:
        valor = input('Qual valor entrará na conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    
    valor = float(valor)
    return sum([saldo, valor])

def saida(saldo):
    eValido = False
    while eValido == False:
        valor = input('Qual valor sairá da conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    
    valor = float(valor)
    return saldo - valor

def validaCategoria(i, categorias):
    eValido = True
    msg = ''
    eValido, msg = validaNum(i, 0)
    if(eValido == False):
        return(eValido, msg)
    
    i = int(i)

    if(i > len(categorias)):
        eValido = False
        msg = 'Essa categoria não existe!'
        return (eValido, msg)
    
    return (eValido, categorias[i - 1])

    
def categorizar(categorias):
    eValido = False
    print('## Categorias de despesas ##')
    _ = list(map(lambda t: print(f"{t[0]+1} - {t[1]}"), enumerate(categorias)))
    print()
    while eValido == False:
        categoriaIndex = input('Categoria: ')
        eValido, msg = validaCategoria(categoriaIndex, categorias)
        if(eValido == False):
            print(msg)

    return msg


while True:
    imprimirMenu()

    opc = input('Escolha uma Opção: ').strip()
    print()

    match opc:
        case '1': 
            saldo = entrada(saldo)
            print('Novo Saldo: ', saldo)
            time.sleep(3)
        case '2': 
            saldo = saida(saldo)
            categoria = categorizar(categorias)
            print('Novo Saldo: ', saldo, ' Categoria: ', categoria)
            time.sleep(3)
        case '5': 
            os.system('telnet towel.blinkenlights.nl')
        case "0": 
            print("→ Saindo...")
            raise SystemExit
        case _:  
            print("Opção inválida.")
            time.sleep(3)
