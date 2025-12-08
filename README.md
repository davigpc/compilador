# Compilador para a Linguagem P

Este projeto implementa o *front-end* completo de um compilador para a **Linguagem P**, abrangendo as fases de análise léxica, sintática e semântica.

## Funcionalidades Implementadas

* **Análise Léxica:** Reconhecimento de tokens via expressões regulares.
* **Análise Sintática:** Parser Descendente Recursivo (*Recursive Descent Parser*) com recuperação de erros em "Modo Pânico".
* **Análise Semântica:**
    * Verificação de variáveis não declaradas.
    * Verificação de variáveis redeclaradas no mesmo escopo.
    * Gestão de escopos (Global e Local) via Tabela de Símbolos.
* **Geração de AST:** Construção da Árvore de Sintaxe Abstrata exportada em formato JSON.

## Requisitos

* Python 3.8 ou superior.

## Instalação e Execução

Não são necessárias bibliotecas externas além das que vêm com o Python padrão (`sys`, `os`, `json`, `re`, `dataclasses`).

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd compilador-p
    ```

2.  **Crie um arquivo de código-fonte:**
    Crie um arquivo de texto com seu código na linguagem P dentro da pasta `entradas/`, por exemplo, `entradas/exemplo.p`.

3.  **Execute o compilador:**
    O programa recebe o caminho do arquivo de entrada como argumento da linha de comando.

    ```bash
    python main.py entradas/exemplo.p
    ```

## Saídas Geradas

Após a execução, o compilador gera arquivos organizados em duas pastas:

### Pasta `erros/`
Contém os relatórios de erros encontrados durante a compilação.
* `*_lexical_errors.txt`: Lista de caracteres inválidos ou desconhecidos.
* `*_syntactic_errors.txt`: Lista de erros de sintaxe (ex: falta de `;`) e erros semânticos (ex: variável não declarada).

### Pasta `saidas/`
Contém os resultados da compilação bem-sucedida (ou parcial).
* `*_symbol_tables.json`: A Tabela de Símbolos completa, detalhando variáveis e parâmetros de cada função e seus tipos.
* `*_ast.json`: A Árvore de Sintaxe Abstrata (AST) completa do programa em formato hierárquico, ideal para visualização da estrutura do código.

> **Nota:** O prefixo `*` corresponde ao nome do arquivo de entrada (ex: para `soma.p`, o arquivo será `soma_ast.json`).

## Estrutura do Projeto

* `main.py`: Orquestrador que liga todas as etapas.
* `lexer.py`: Analisador Léxico.
* `parser.py`: Analisador Sintático e Semântico.
* `ast_nodes.py`: Definição das classes da Árvore (AST).
* `symbol_table.py`: Gestão da Tabela de Símbolos e Escopos.
