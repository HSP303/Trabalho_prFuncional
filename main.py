import os
import time
import csv
import ast
from datetime import date

ARQUIVO_DADOS = "dados.csv"

categorias = ['Contas', 'Superficial']
meta = 10000
saldo = 0
extrato = []

def _serializar_extrato_item(item):
    conv = []
    for x in item:
        if isinstance(x, date):
            conv.append(x.isoformat())
        else:
            conv.append(x)
    return conv

def save_state(saldo, meta, categorias, extrato, arquivo=ARQUIVO_DADOS):
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#versao", 1])
        w.writerow(["CONFIG", "SALDO", saldo])
        w.writerow(["CONFIG", "META", meta])
        for cat in categorias:
            w.writerow(["CATEGORIA", cat])
        for item in extrato:
            w.writerow(["EXTRATO", repr(_serializar_extrato_item(item))])

def load_state(saldo_padrao, meta_padrao, categorias_padrao, extrato_padrao, arquivo=ARQUIVO_DADOS):
    if not os.path.exists(arquivo):
        return saldo_padrao, meta_padrao, categorias_padrao, extrato_padrao

    saldo = saldo_padrao
    meta = meta_padrao
    categorias = []
    extrato = []

    try:
        with open(arquivo, "r", newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            for row in r:
                if not row: 
                    continue
                t = row[0]
                if t == "#versao":
                    continue
                if t == "CONFIG" and len(row) >= 3:
                    if row[1] == "SALDO":
                        try: saldo = float(row[2])
                        except: pass
                    elif row[1] == "META":
                        try: meta = int(float(row[2]))
                        except: pass
                elif t == "CATEGORIA" and len(row) >= 2:
                    categorias.append(row[1])
                elif t == "EXTRATO" and len(row) >= 2:
                    try:
                        item = ast.literal_eval(row[1]) 
                        extrato.append(item)
                    except:
                        extrato.append([row[1]])
    except:
        return saldo_padrao, meta_padrao, categorias_padrao, extrato_padrao

    if not categorias:
        categorias = categorias_padrao[:]
    return saldo, meta, categorias, extrato

def imprimirMenu():
    try:
        os.system('clear')
    except:
        os.system('cls')
    print("""
=== MENU ===
1 - Entrada
2 - Saída
3 - Cadastrar Meta
4 - Cadastrar Categoria    
5 - Mostrar Extrato
6 - Sair do Tédio (Precisa ter o telnet instalado e no PATH)
7 - Salvar Dados
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
    return (sum([saldo, valor]), valor)

def saida(saldo):
    eValido = False
    while eValido == False:
        valor = input('Qual valor sairá da conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    
    valor = float(valor)
    return ((saldo - valor), valor)

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

def listarExtrato(extrato):
    try:
        os.system('clear')
    except:
        os.system('cls')
    print('=== Extrato ===')
    for linha in extrato:
        print(f'# {linha}')
    print('===============')

saldo, meta, categorias, extrato = load_state(saldo, meta, categorias, extrato)

while True:
    imprimirMenu()

    opc = input('Escolha uma Opção: ').strip()
    print()

    match opc:
        case '1': 
            saldo, valor = entrada(saldo)
            print('Novo Saldo: ', saldo)
            extrato.append(['Valor:', valor, ' Saldo: ', saldo, ' - ', date.today()])
            time.sleep(3)
        case '2': 
            saldo, valor = saida(saldo)
            categoria = categorizar(categorias)
            print('Novo Saldo: ', saldo, ' Categoria: ', categoria)
            extrato.append(['Valor:', (valor * -1), ' Categoria: ', categoria, ' Saldo: ', saldo, ' - ', date.today()])
            time.sleep(3)
        case '5':
            listarExtrato(extrato)
            input('[Precione Enter]')
        case '6': 
            os.system('telnet towel.blinkenlights.nl')
        case '7':
            save_state(saldo, meta, categorias, extrato)
            print("Dados salvos em", ARQUIVO_DADOS)
            time.sleep(2)
        case "0": 
            print("→ Saindo...")
            raise SystemExit
        case _:  
            print("Opção inválida.")
            time.sleep(3)