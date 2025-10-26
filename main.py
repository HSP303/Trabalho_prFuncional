import os
import time
import re

categorias = ['Contas', 'Superficial']
meta = 10000
saldo = 0

meta_nome = 'Objetivo'
meta_prazo = ''  # opcional

metas_por_categoria = {}       # ex.: {"Alimentação": 800.0}
gastos_por_categoria = {}      # acumulador "geral" (legado)
gastos_cat_por_periodo = {}    # ex.: {"2025-10": {"Alimentação": 350.0}}
ultimo_movimento_valor = 0.0   # armazena o valor da última saída

periodo_atual = ""

def imprimirMenu():
    #os.system('clear')
    print("""
=== MENU ===
1 - Entrada
2 - Saída
3 - Cadastrar Meta
4 - Cadastrar Categoria
5 - Sair do Tédio (Precisa ter o telnet instalado e no PATH)
6 - Ver Atingimento de Metas (mês)
7 - Selecionar Período (YYYY-MM)
8 - Top 3 gastos no mês
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
    global ultimo_movimento_valor
    eValido = False
    while eValido == False:
        valor = input('Qual valor sairá da conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    valor = float(valor)
    ultimo_movimento_valor = valor
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

def cadastrarMeta():
    global meta, meta_nome, meta_prazo
    nome = input("Nome da meta (ex.: Viagem, Carro): ").strip()
    if nome:
        meta_nome = nome

    eValido = False
    while eValido == False:
        valor = input('Qual valor deseja alcançar? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    meta = float(valor)

    prazo = input("Prazo (opcional YYYY-MM): ").strip()
    if prazo:
        meta_prazo = prazo

    print(f"Meta definida: {meta_nome} | alvo R$ {meta:.2f}" + (f" | prazo {meta_prazo}" if meta_prazo else ""))
    mostrarProgresso()

def mostrarProgresso():
    if meta and meta > 0:
        perc = (saldo / meta) * 100
        restante = meta - saldo
        if restante < 0: restante = 0
        print(f"Progresso da meta '{meta_nome}': {perc:.2f}% | faltam R$ {restante:.2f}")
    else:
        print("Sem meta definida")

def alertarMeta():
    if meta and meta > 0:
        perc = (saldo / meta) * 100
        if perc >= 100:
            print(f"[META] '{meta_nome}' alcançada com êxito")
        elif perc >= 90:
            print(f"[ALERTA] meta: '{meta_nome}' em {perc:.1f}% do objetivo.")

def cadastrarMetaCategoria():
    cat = categorizar(categorias)
    if not isinstance(cat, str):
        return
    eValido = False
    while eValido == False:
        v = input(f"Meta (valor alvo) para a categoria '{cat}': ")
        eValido, msg = validaNum(v, 1)
        print(msg)
    metas_por_categoria[cat] = float(v)
    print(f"Meta da categoria '{cat}' definida em R$ {metas_por_categoria[cat]:.2f}")

def alertarMetaCategoria(cat):
    if cat in metas_por_categoria:

        gastos_mes = gastos_cat_por_periodo.get(periodo_atual, {})
        gasto = gastos_mes.get(cat, 0.0)
        alvo  = metas_por_categoria[cat]
        if alvo > 0:
            perc = (gasto / alvo) * 100
            if perc >= 100:
                print(f"[META/CATEGORIA] '{cat}' estourou a meta! ({perc:.1f}%)")
            elif perc >= 90:
                print(f"[ALERTA/CATEGORIA] '{cat}' em {perc:.1f}% da meta.")

def cadastrarCategoria():
    global categorias
    nome = input("Nome da nova categoria: ").strip()
    if not nome:
        print("Categoria inválida.")
        return
    if nome in categorias:
        print("Categoria já existe.")
        return
    categorias.append(nome)
    print("Categoria cadastrada:", nome)
    print("Categorias atuais:", ", ".join(categorias))


def validarPeriodo(s):
    if not re.fullmatch(r"\d{4}-\d{2}", s or ""):
        return False
    ano, mes = s.split("-")
    try:
        m = int(mes)
        return 1 <= m <= 12
    except:
        return False

def selecionarPeriodo(inicial=False):
    global periodo_atual
    padrao = time.strftime("%Y-%m")
    if inicial:
        s = input(f"Informe o período atual (YYYY-MM) [Enter = {padrao}]: ").strip()
        if not s:
            periodo_atual = padrao
            print("Período atual definido:", periodo_atual)
            return
    else:
        s = input("Informe o novo período (YYYY-MM): ").strip()
    if validarPeriodo(s):
        periodo_atual = s
        print("Período atual definido:", periodo_atual)
    else:
        print("Período inválido. Mantido:", periodo_atual or padrao)
        if not periodo_atual:
            periodo_atual = padrao

def verAtingimentoMetasDoMes():
    #Esta função só exibe, o cálculo vem da função pura
    print(f"=== Atingimento de metas (período {periodo_atual}) ===")
    gastos_mes = gastos_cat_por_periodo.get(periodo_atual, {})
    if not metas_por_categoria:
        print("(Sem metas por categoria definidas)")
        return
    for cat, alvo in metas_por_categoria.items():
        gasto = gastos_mes.get(cat, 0.0)
        perc = (gasto / alvo * 100) if alvo > 0 else 0.0
        print(f"- {cat}: gasto R$ {gasto:.2f} / meta R$ {alvo:.2f} ({perc:.1f}%)")

def verTop3GastosDoMes():
    #Essa função só exibe, o cálculo vem da função pura
    print(f"=== Top-3 gastos por categoria (período {periodo_atual}) ===")
    gastos_mes = gastos_cat_por_periodo.get(periodo_atual, {})
    if not gastos_mes:
        print("(Sem despesas neste período)")
        return
    ordenado = sorted(gastos_mes.items(), key=lambda kv: kv[1], reverse=True)[:3]
    for i, (cat, tot) in enumerate(ordenado, 1):
        print(f"{i}) {cat}: R$ {tot:.2f}")

selecionarPeriodo(inicial=True)

while True:
    imprimirMenu()
    print(f"(Período atual: {periodo_atual})")  # feedback rápido

    opc = input('Escolha uma Opção: ').strip()
    print()

    match opc:
        case '1':
            saldo = entrada(saldo)
            print('Novo Saldo: ', saldo)
            alertarMeta()
            time.sleep(1)
        case '2':
            saldo = saida(saldo)
            categoria = categorizar(categorias)

            gastos_por_categoria[categoria] = gastos_por_categoria.get(categoria, 0.0) + ultimo_movimento_valor

            # para atender "agregações por mês e categoria"
            gastos_cat_por_periodo.setdefault(periodo_atual, {})
            gastos_cat_por_periodo[periodo_atual][categoria] = gastos_cat_por_periodo[periodo_atual].get(categoria, 0.0) + ultimo_movimento_valor

            alertarMetaCategoria(categoria)
            print('Novo Saldo: ', saldo, ' Categoria: ', categoria)
            time.sleep(1)
        case '3':
            print("a) Meta GLOBAL (objetivo: Viagem/Carro)")
            print("b) Meta POR CATEGORIA")
            esc = input("Escolha (a/b): ").strip().lower()
            if esc == 'b':
                cadastrarMetaCategoria()
            else:
                cadastrarMeta()
            time.sleep(1)
        case '4':
            cadastrarCategoria()
            time.sleep(1)
        case '5':
            os.system('telnet towel.blinkenlights.nl')
        case '6':
            verAtingimentoMetasDoMes()
            time.sleep(1)
        case '7':
            selecionarPeriodo(inicial=False)
            time.sleep(1)
        case '8':
            verTop3GastosDoMes()
            time.sleep(1)
        case "0":
            print("→ Saindo...")
            raise SystemExit
        case _:
            print("Opção inválida.")
            time.sleep(1)
