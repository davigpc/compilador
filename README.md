# Compilador para a Linguagem P

Este projeto implementa o front-end de um compilador para a linguagem P.

## Requisitos

- Python 3.8 ou superior

## Instalação e Execução

Não são necessárias bibliotecas externas além das que vêm com o Python padrão.

1.  **Clone o repositório (ou crie os arquivos):**
    ```bash
    git clone <url-do-seu-repositorio>
    cd compilador-p
    ```

2.  **Crie um arquivo de código-fonte:**
    Crie um arquivo de texto com seu código na linguagem P, por exemplo, `input.p`.

3.  **Execute o analisador:**
    O programa recebe o caminho do arquivo de entrada como argumento da linha de comando.

    ```bash
    python main.py input.p
    ```

4.  **Verifique a Saída:**
    Após a execução, dois arquivos serão gerados no mesmo diretório:
    * `tokens.txt`: Contém a lista de todos os tokens reconhecidos.
    * `lexical_errors.txt`: Contém a lista de todos os erros léxicos encontrados, com a linha e o caractere inválido.