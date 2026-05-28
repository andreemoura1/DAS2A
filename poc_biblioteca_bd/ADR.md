# ADR — Escolha de Biblioteca para Conexão com Banco de Dados

**Data:** 2026-05-28  
**Status:** Aceito  
**Projeto:** DAS2A — VendaMais Distribuidora  
**Contexto da PoC:** `poc_biblioteca_bd` / Azure Function `GET /api/poc-benchmark`

---

## Contexto

O projeto DAS2A utiliza Azure Functions (triggers) para extrair dados do ERP SQL Server da VendaMais Distribuidora. Cada trigger executa um `SELECT *` em uma tabela do ERP e carrega todas as linhas na memória para posterior transformação e carga.

A equipe identificou a necessidade de validar empiricamente qual abordagem de biblioteca de banco de dados oferece melhor desempenho para esse padrão de uso: **leitura em massa de tabelas inteiras** (operação ETL pura, sem escrita complexa ou ORM mapeado).

Foram avaliadas duas abordagens:

| Abordagem | Biblioteca | Descrição |
|---|---|---|
| Driver Nativo | `sqlite3` (Python built-in) | Acesso direto ao banco, sem camadas intermediárias. Equivalente ao `pyodbc` usado em produção no DAS2A. |
| ORM / Toolkit | `SQLAlchemy 2.x` | Camada de abstração sobre o driver nativo, com connection pool, dialetos e query builder. |

---

## Metodologia da PoC

A PoC foi implementada como uma **Azure Function HTTP Trigger** (`GET /api/poc-benchmark`) dentro do projeto DAS2A, em `src/triggers/poc_benchmark.py`.

- **Banco de dados:** SQLite local em diretório temporário (`tempfile.gettempdir()`)
- **Tabela:** `cliente` — espelha a estrutura do ERP do DAS2A
- **Volumetria:** 2.000 registros
- **Operação:** `SELECT * FROM cliente` + `fetchall()` (todas as linhas carregadas na memória)
- **Repetições:** 2 execuções por biblioteca
- **Métrica:** `time.perf_counter()` — cronômetro de alta resolução do Python
- **Resultado:** Tempo médio das 2 execuções por biblioteca

---

## Resultados Medidos

| Métrica | `sqlite3` (nativo) | `SQLAlchemy 2.x` |
|---|---|---|
| Execução 1 | 0.002824s | 0.003219s |
| Execução 2 | 0.002963s | 0.004892s |
| **Tempo médio** | **0.002894s** | **0.004056s** |
| Camadas de abstração | 1 (driver direto) | 3 (pool + dialeto + sqlite3) |

**Diferença:** `sqlite3` (nativo) foi **~29% mais rápido** que `SQLAlchemy` para a mesma operação de leitura em massa.

---

## Decisão

**Utilizar driver nativo (`pyodbc` em produção / `sqlite3` em testes locais) para as operações de extração do DAS2A.**

---

## Justificativas

1. **Desempenho superior comprovado:** O driver nativo foi ~29% mais rápido no cenário idêntico ao dos triggers do DAS2A (SELECT em massa + fetchall).

2. **Sem overhead desnecessário:** O SQLAlchemy adiciona três camadas (connection pool, dialeto, driver) úteis em sistemas com ORM mapeado e CRUD complexo — mas que representam custo puro em pipelines ETL de leitura.

3. **Alinhamento com o padrão já adotado:** O DAS2A já usa `pyodbc` (driver nativo para SQL Server) nos triggers de extração. Manter esse padrão garante consistência arquitetural e facilita onboarding de novos desenvolvedores.

4. **Zero dependências extras:** `sqlite3` é embutido no Python; `pyodbc` é a única dependência necessária em produção.

5. **Simplicidade:** Para a operação de ETL (abrir conexão → executar SELECT → fechar conexão), o modelo direto do driver nativo é mais legível e direto ao ponto.

---

## Quando o SQLAlchemy seria a escolha correta

O SQLAlchemy se justificaria em cenários diferentes do DAS2A, como:

- Sistemas com múltiplas entidades mapeadas via ORM (modelos Python ↔ tabelas)
- Aplicações com operações CRUD complexas e relacionamentos entre entidades
- Projetos que precisam trocar de banco de dados sem alterar o código (abstração de dialeto)
- APIs REST com camada de serviço e repositório usando Session/Query do SQLAlchemy

---

## Consequências

- **Positivas:** Menor latência nas extrações, código mais simples, sem dependências extras além do `pyodbc` já existente.
- **Negativas / Aceitas:** Ausência de abstração — qualquer troca de banco de dados requer ajuste direto nas queries. Aceito porque o DAS2A está fixado no SQL Server e não há previsão de migração.
- **Ação:** Manter `pyodbc` nos triggers de extração do DAS2A e documentar esse padrão no guia de contribuição do projeto.
