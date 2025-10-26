# Orçamento Familiar — (Python)

Projeto da disciplina **Linguagem de Programação e Paradigmas** — **Sistemas de Informação**  
Professor: **Ademar Perfoll Junior**

Aplicação de terminal para controle de **orçamento familiar** com:
- **Categorias**, **metas (global e por categoria)** e **alertas**
- **Lançamentos** de **receitas** e **despesas**
- **Relatórios** por **mês e categoria**, incluindo **Top-3 gastos**
- Checagem do **invariante** `soma(receitas) − soma(despesas) == saldo`

Autores: **Pedro Henrique Scheidt** e **Vinícius Minas**

---

## Sumário
- [Requisitos](#requisitos)
- [Como executar](#como-executar)
- [Funcionalidades](#funcionalidades)
- [Uso (passo a passo)](#uso-passo-a-passo)
- [Relatórios e agregações](#relatórios-e-agregações)
- [Validações e invariantes](#validações-e-invariantes)
- [Programação Funcional aplicada](#programação-funcional-aplicada)
- [Testes rápidos](#testes-rápidos)
- [Persistência (CSV)](#persistência-csv)
- [Futuras melhorias](#futuras-melhorias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Créditos](#créditos)

---
## Requisitos

- **Python 3.10+** (testado com Python 3.13.1).
- Sistema operacional: Windows / Linux / macOS (CLI).
- Nenhuma dependência externa.

---

## Como executar

Na raiz do projeto:

```bash
python main.py
```

> Dica (Windows): se aparecer a mensagem `'clear' is not recognized...` é apenas a limpeza de tela tentando usar `clear`. Isso **não afeta** o funcionamento (opcionalmente, você pode trocar por `cls` no código).

---

## Funcionalidades

- **Entradas e saídas** de valores (receitas/despesas).
- **Classificação por categoria** em toda saída.
- **Cadastro de categoria** (evita duplicar).
- **Metas**:
  - **Global** (um valor alvo geral).
  - **Por categoria** (alvos específicos por categoria).
  - **Alertas** automáticos por categoria (≥90% e ≥100% do alvo).
- **Relatórios por período (YYYY-MM)**:
  - **Saldo do período** (receitas − despesas).
  - **Gastos por categoria** e **Top-3** categorias no mês.
  - **Atingimento de metas por categoria**.
  - Verificação do **invariante** `receitas − despesas == Δsaldo`.
- **Persistência** em `dados.csv` (saldo, meta global, categorias, extrato).

> Obs.: as **metas por categoria** são mantidas **em memória**.

---

## Uso (passo a passo)

Ao iniciar, o menu principal:

```
1 - Entrada
2 - Saída
3 - Cadastrar Meta
4 - Cadastrar Categoria
5 - Mostrar Extrato
6 - Sair do Tédio (telnet)
7 - Salvar Dados
0 - Sair
```

- **1 – Entrada**: registra receitas (valores **não negativos**; `0` é aceito).
- **2 – Saída**: registra despesas (valores **não negativos**; `0` é aceito) e **pede a categoria** (índice **> 0**).  
  Após cada saída, se existir meta para a categoria, são exibidos **alertas** (≥90% e ≥100%).
- **3 – Cadastrar Meta**:
  - `a` → **Meta Global** (valor alvo).
  - `b` → **Meta por Categoria** (define alvo para a categoria escolhida).
- **4 – Cadastrar Categoria**: adiciona nova categoria (evita duplicar, case-sensitive).
- **5 – Mostrar Extrato**: imprime o extrato e, em seguida, solicita um **período** (`YYYY-MM`) para gerar o **relatório** (ver abaixo).
- **7 – Salvar Dados**: persiste saldo, meta global, categorias e extrato em `dados.csv`.

---

## Relatórios e agregações

Na opção **5 – Mostrar Extrato**, ao informar um período (ou apenas Enter para o mês atual) a aplicação exibe:

- **Receitas**, **Despesas** e **Saldo do período**.
- **Top-3 gastos por categoria** no mês.
- **Atingimento de metas por categoria** (com etiquetas de alerta/atingimento).
- **Invariante**: compara `receitas − despesas` com `Δsaldo` (variação do saldo no mês).  
  Exibe **OK** quando consistente.

---

## Validações e invariantes

- **Valores monetários**: **não negativos** (aceita `0`), conforme proposta.
- **Índices de categoria**: **> 0** (evita seleção inválida/negativa).
- **Invariante** por período: `soma(receitas) − soma(despesas) == Δsaldo`.

---

## Programação Funcional aplicada

**Funções puras (sem efeitos colaterais, imutáveis):**
- `definir_meta_puro(meta_atual, valor_numerico) -> float`  
  Retorna **nova meta global**.
- `definir_meta_categoria_puro(metas_dict, categoria, valor_numerico) -> dict`  
  Retorna **novo dicionário** de metas por categoria (não muta o original).
- `adicionar_categoria_puro(categorias_atual, nome) -> list`  
  Retorna **nova lista** de categorias (não muta a original).
- `resumo_periodo_puro(extrato, periodo_yyyy_mm) -> dict`  
  Calcula **receitas**, **despesas**, **saldo do período**, **gastos por categoria**, **Top-3** e **Δsaldo** do período.
- `atingimento_metas_categoria_puro(metas_por_cat, gastos_por_cat_periodo) -> list`  
  Calcula o percentual de atingimento por categoria.

**Uso de funções de ordem superior:**
- `sorted(..., key=lambda ...)` para ordenação funcional do Top-3.
- `map` é usado pontualmente para impressão de categorias.

> A imutabilidade é respeitada retornando **novas estruturas** (listas/dicts) nas funções de cadastro e metas; a integração com a interface mantém o estado da aplicação no loop, sem que as funções puras dependam de variáveis globais.

---

## Testes rápidos

### 1) Roteiro manual
1. **4** → Cadastrar Categoria → `Alimentação`.  
2. **3** → Cadastrar Meta → `b` (por categoria) → selecionar **Alimentação** → meta `800`.  
3. **1** → Entrada: `1000`.  
4. **2** → Saída: `500` → categoria **Alimentação**.  
5. **2** → Saída: `220` → categoria **Alimentação** → deve aparecer **alerta ≥90%**.  
6. **5** → Extrato → informe o **mês atual** → ver:  
   - Receitas `1000.00`, Despesas `720.00`, Saldo período `280.00`.  
   - Top-3 com **Alimentação**.  
   - Atingimento **90%** para Alimentação.  
   - **Invariante OK**.


---

## Persistência (CSV)

Arquivo: `dados.csv`  
São persistidos:
- `SALDO` (float)
- `META` global (int/float)
- **Categorias** (linhas `CATEGORIA`)
- **Extrato** (linhas `EXTRATO`, com data ISO)

> **Metas por categoria** (**não** são persistidas).

---

## Futuras melhorias

- **Persistir metas por categoria** (ex.: gravar como `METACAT, categoria, valor` no CSV).  
- **Validação de período** também na entrada inicial (hoje o relatório já valida).  
- **Exportar relatório** para CSV/JSON (extra).

---

## Estrutura do projeto

```
.
├─ main.py          # aplicativo CLI
└─ dados.csv        # gerado em tempo de execução (persistência)
```

---

## Créditos

- **Autores**: Pedro Henrique Scheidt e Vinícius Minas
- **Curso**: Sistemas de Informação — Linguagem de Programação e Paradigmas  
- **Professor**: Ademar Perfoll Junior
