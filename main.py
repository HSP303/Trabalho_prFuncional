import os
import time
import csv
import ast
from datetime import date, datetime

ARQUIVO_DADOS = "dados.csv"

categorias = ['Contas', 'Superficial']
meta = 10000
saldo = 0
extrato = []

metas_por_categoria = {} 

def _serializar_extrato_item(item):
    conv = []
    for x in item:
        if isinstance(x, date):
            conv.append(x.isoformat())
        else:
            conv.append(x)
    return conv

# função para salvar o extrato e algumas variáveis em um arquivo CSV
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

#  Função para carregar as informações do CSV
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
                        try:
                            saldo = float(row[2])
                        except:
                            pass
                    elif row[1] == "META":
                        try:
                            meta = int(float(row[2]))
                        except:
                            pass
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

# Função para printar o menu na tela
def imprimirMenu(saldo):
    try:
        os.system('clear')
    except:
        os.system('cls')
    print(f"""
============= MENU =============
Alunos: Pedro Henrique Scheidt e Vinícius Antônio Minas
Saldo em conta: {saldo}
1 - Entrada
2 - Saída
3 - Cadastrar Meta
4 - Cadastrar Categoria    
5 - Mostrar Extrato
6 - Sair do Tédio (Precisa ter o telnet instalado e no PATH)
7 - Salvar Dados
0 - Sair
    """)

# Função para validar entradas de valores numéricos (Inteiro ou Float)
def validaNum(valor, floatInt):

    try:
        if floatInt == 1:
            valor = float(valor)
        else:
            valor = int(valor)
    except:
        return (False, 'O valor não é um número. Digite um valor válido!')

    if floatInt == 1:
        if valor < 0:
            return (False, 'Digite um valor não negativo!')
    else:
        if valor <= 0:
            return (False, 'Digite um valor maior que zero!')

    return (True, '')

# Função para retornar a soma do saldo com um valor inserido pelo usuário
def entrada(saldo):
    eValido = False
    while eValido == False:
        valor = input('Qual valor entrará na conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    valor = float(valor)
    return (sum([saldo, valor]), valor)

# Função para retornar a subtração do saldo com um valor inserido pelo usuário
def saida(saldo):
    eValido = False
    while eValido == False:
        valor = input('Qual valor sairá da conta? ')
        eValido, msg = validaNum(valor, 1)
        print(msg)
    valor = float(valor)
    return ((saldo - valor), valor)

# Verificar a categoria que o usuário insere
def validaCategoria(i, categorias):
    eValido, msg = validaNum(i, 0)
    if not eValido:
        return (False, msg)
    i = int(i)
    if i > len(categorias):
        return (False, 'Essa categoria não existe!')
    return (True, categorias[i - 1])

# Função para o usuário inserir a categoria da saída de valor da conta
def categorizar(categorias):
    eValido = False
    print('## Categorias de despesas ##')
    _ = list(map(lambda t: print(f"{t[0] + 1} - {t[1]}"), enumerate(categorias)))
    print()
    while eValido == False:
        categoriaIndex = input('Categoria: ')
        eValido, msg = validaCategoria(categoriaIndex, categorias)
        if (eValido == False):
            print(msg)
    return msg

# Função para listar o extrato na tela
def listarExtrato(extrato):
    try:
        os.system('clear')
    except:
        os.system('cls')
    print('=== Extrato ===')
    for linha in extrato:
        print(f'# {linha}')
    print('===============')

    periodo = input("Ver RESUMO por período (YYYY-MM) [Enter = mês atual]: ").strip()
    if not periodo:
        hoje = date.today()
        periodo = f"{hoje.year:04d}-{hoje.month:02d}"
    if not _validar_periodo(periodo):
        print("Período inválido. (Use YYYY-MM)")
        return

    resumo = resumo_periodo_puro(extrato, periodo)
    print(f"\n=== Resumo do período {periodo} ===")
    print(
        f"Receitas: R$ {resumo['receitas']:.2f} | Despesas: R$ {resumo['despesas']:.2f} | Saldo do período: R$ {resumo['saldo_periodo']:.2f}")

    # Top-3 gastos
    if resumo['top3']:
        print("\nTop-3 gastos por categoria:")
        for i, (cat, tot) in enumerate(resumo['top3'], 1):
            print(f"{i}) {cat}: R$ {tot:.2f}")
    else:
        print("\nTop-3 gastos por categoria: (sem despesas no período)")

    # Atingimento de metas por categoria
    if metas_por_categoria:
        print("\nAtingimento de metas por categoria:")
        linhas = atingimento_metas_categoria_puro(metas_por_categoria, resumo['gastos_por_categoria'])
        for cat, gasto, alvo, perc in linhas:
            alert = ""
            if perc >= 100:
                alert = "  [META/CATEGORIA atingida]"
            elif perc >= 90:
                alert = "  [ALERTA ≥90%]"
            print(f"- {cat}: gasto R$ {gasto:.2f} / meta R$ {alvo:.2f} ({perc:.1f}%)" + alert)
    else:
        print("\nAtingimento de metas por categoria: (sem metas definidas)")

    # Invariante no período
    ok = abs((resumo['receitas'] - resumo['despesas']) - resumo['delta_saldo']) < 1e-6
    status = "OK" if ok else "QUEBRA"
    print(f"\nInvariante (receitas - despesas == Δsaldo): {status}")
    print(f"   receitas - despesas = R$ {resumo['receitas'] - resumo['despesas']:.2f}")
    print(f"   Δsaldo = R$ {resumo['delta_saldo']:.2f}")


# ----------------- Funções puras / imutáveis em metas e categorias -----------------
def definir_meta_puro(meta_atual, valor_numerico):
    # PURA: retorna nova meta global (float).
    return float(valor_numerico)

def definir_meta_categoria_puro(metas_dict, categoria, valor_numerico):
    # Pura/imutável: retorna novo dict de metas por categoria.
    return {**metas_dict, categoria: float(valor_numerico)}

def adicionar_categoria_puro(categorias_atual, nome):
    # Pura/imutável: retorna nova lista (não muta a original).
    nome_norm = (nome or "").strip()
    if not nome_norm:
        return categorias_atual
    if nome_norm in categorias_atual:
        return categorias_atual
    return categorias_atual + [nome_norm]

def _validar_periodo(s):
    try:
        if len(s) != 7 or s[4] != '-':
            return False
        y, m = s.split('-')
        y = int(y);
        m = int(m)
        return 1 <= m <= 12
    except:
        return False

def _parse_data(obj):
    if isinstance(obj, date):
        return obj
    if isinstance(obj, str) and len(obj) == 10 and obj[4] == '-' and obj[7] == '-':
        try:
            return date.fromisoformat(obj)
        except:
            return None
    return None

def _parse_item(item):
    # Pura: extrai valor, categoria (ou None), saldo e data de um item do extrato.
    valor = None
    categoria = None
    saldo_linha = None
    data_linha = None
    for i, x in enumerate(item):
        if x == 'Valor:' and i + 1 < len(item):
            try:
                valor = float(item[i + 1])
            except:
                pass
        if isinstance(x, str) and x.strip() == 'Categoria:' and i + 1 < len(item):
            categoria = item[i + 1]
        if isinstance(x, str) and x.strip() == 'Saldo:' and i + 1 < len(item):
            try:
                saldo_linha = float(item[i + 1])
            except:
                pass
        if i == len(item) - 1:
            data_linha = _parse_data(x)
    return {
        'valor': valor if valor is not None else 0.0,
        'categoria': categoria,
        'saldo': saldo_linha if saldo_linha is not None else 0.0,
        'data': data_linha,
    }


def resumo_periodo_puro(extrato, periodo_yyyy_mm):
    # função pura: computa receitas, despesas, top 3, gastos por categoria e  saldo no período.
    regs = []
    for it in extrato:
        r = _parse_item(it)
        if r['data'] is None:
            continue
        mes = f"{r['data'].year:04d}-{r['data'].month:02d}"
        if mes == periodo_yyyy_mm:
            regs.append(r)

    receitas = sum(r['valor'] for r in regs if r['valor'] > 0)
    despesas = sum((-r['valor']) for r in regs if r['valor'] < 0)

    # gastos por categoria (somente despesas)
    gastos_por_categoria = {}
    for r in regs:
        if r['valor'] < 0 and r['categoria']:
            gastos_por_categoria[r['categoria']] = gastos_por_categoria.get(r['categoria'], 0.0) + (-r['valor'])

    # top-3
    top3 = sorted(gastos_por_categoria.items(), key=lambda kv: kv[1], reverse=True)[:3]

    # delta de saldo do período, estimando saldo antes do 1º lançamento do mês
    if regs:
        regs_ordenado = regs  # já estão na ordem de inserção
        saldo_depois_primeiro = regs_ordenado[0]['saldo']
        valor_primeiro = regs_ordenado[0]['valor']
        saldo_antes_primeiro = saldo_depois_primeiro - valor_primeiro
        saldo_fim = regs_ordenado[-1]['saldo']
        delta_saldo = saldo_fim - saldo_antes_primeiro
    else:
        delta_saldo = 0.0

    return {
        'receitas': receitas,
        'despesas': despesas,
        'saldo_periodo': receitas - despesas,
        'gastos_por_categoria': gastos_por_categoria,
        'top3': top3,
        'delta_saldo': delta_saldo,
    }


def atingimento_metas_categoria_puro(metas_por_cat, gastos_por_cat_periodo):
    # PURA: retorna lista (cat, gasto, meta, %) para exibição de metas por categoria.
    linhas = []
    for cat, meta_cat in metas_por_cat.items():
        gasto = gastos_por_cat_periodo.get(cat, 0.0)
        perc = (gasto / meta_cat * 100.0) if meta_cat > 0 else 0.0
        linhas.append((cat, gasto, meta_cat, round(perc, 1)))
    return linhas


# -----------------Ações que utilizam as funções puras -----------------
def mostrarProgresso(meta_valor, saldo_atual):
    if meta_valor and meta_valor > 0:
        perc = (saldo_atual / meta_valor) * 100
        restante = meta_valor - saldo_atual
        if restante < 0:
            restante = 0
        print(f"Progresso da meta: {perc:.2f}% | faltam R$ {restante:.2f}")
    else:
        print("(Sem meta definida)")

def cadastrarMeta(meta, metas_por_categoria):
    print("a) Meta GLOBAL (valor-alvo)")
    print("b) Meta POR CATEGORIA")
    tipo = input("Escolha (a/b): ").strip().lower()

    if tipo == 'b':
        cat = categorizar(categorias)
        if not isinstance(cat, str):
            return
        eValido = False
        while eValido == False:
            v = input(f"Meta (valor não-negativo) para '{cat}': ")
            eValido, msg = validaNum(v, 1)
            print(msg)
        metas_por_categoria = definir_meta_categoria_puro(metas_por_categoria, cat, v)
        print(f"Meta da categoria '{cat}' definida em R$ {metas_por_categoria[cat]:.2f}")
    else:
        eValido = False
        while eValido == False:
            v = input('Qual valor deseja alcançar (global)? ')
            eValido, msg = validaNum(v, 1)
            print(msg)
        meta = definir_meta_puro(meta, v)
        prazo = input("Prazo (opcional YYYY-MM): ").strip()
        if prazo:
            print(f"Meta GLOBAL definida: R$ {meta:.2f} | prazo {prazo}")
        else:
            print(f"Meta GLOBAL definida: R$ {meta:.2f}")
        mostrarProgresso(meta, saldo)
    return (meta, metas_por_categoria)

def cadastrarCategoria(categorias):
    nome = input("Nome da nova categoria: ").strip()
    if not nome:
        print("Categoria inválida.")
        return
    if nome in categorias:
        print("Categoria já existe.")
        return
    return adicionar_categoria_puro(categorias, nome)  # imutável
    print("Categoria cadastrada:", nome)
    print("Categorias atuais:", ", ".join(categorias))

def _alertar_meta_categoria_pos_saida(extrato, categoria):
    # usa mês atual para alertar imediatamente após a saída
    hoje = date.today()
    periodo = f"{hoje.year:04d}-{hoje.month:02d}"
    res = resumo_periodo_puro(extrato, periodo)
    if categoria in metas_por_categoria:
        gasto = res['gastos_por_categoria'].get(categoria, 0.0)
        alvo = metas_por_categoria[categoria]
        if alvo > 0:
            perc = (gasto / alvo) * 100.0
            if perc >= 100:
                print(f"[META/CATEGORIA] '{categoria}' estourou a meta! ({perc:.1f}%)")
            elif perc >= 90:
                print(f"[ALERTA/CATEGORIA] '{categoria}' em {perc:.1f}% da meta.")

saldo, meta, categorias, extrato = load_state(saldo, meta, categorias, extrato)

while True:
    imprimirMenu(saldo)

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
            # alerta de meta por categoria (somente cálculo, não persiste nada)
            _alertar_meta_categoria_pos_saida(extrato, categoria)
            time.sleep(3)

        case '3':
            meta, metas_por_categoria = cadastrarMeta(meta, metas_por_categoria)
            time.sleep(2)

        case '4':
            categorias = cadastrarCategoria(categorias)
            time.sleep(2)

        case '5':
            listarExtrato(extrato)
            input('[Pressione Enter]')

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
