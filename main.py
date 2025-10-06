import sys
import os
from lexer import Lexer, Token


def write_to_file(filename: str, content: list):
    """Escreve o conteúdo de uma lista em um arquivo, um item por linha."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if not content:
                f.write("")  # Garante que o arquivo seja criado mesmo se estiver vazio
            else:
                for item in content:
                    f.write(str(item) + '\n')
        print(f"Saída escrita com sucesso em '{filename}'.")
    except IOError as e:
        print(f"Erro ao escrever no arquivo '{filename}': {e}")


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <caminho_para_arquivo_fonte>")
        sys.exit(1)

    source_file_path = sys.argv[1]

# ========= LEITURA ========= #
    TOKENS_DIR = "saidas"
    ERRORS_DIR = "erros"

    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(ERRORS_DIR, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(source_file_path))[0]

    tokens_output_file = os.path.join(TOKENS_DIR, f"{base_name}_tokens.txt")
    errors_output_file = os.path.join(ERRORS_DIR, f"{base_name}_lexical_errors.txt")

    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{source_file_path}' não foi encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        sys.exit(1)

# ================== #

    lexer = Lexer(source_code)
    tokens, errors = lexer.scan_tokens()

    if errors:
        print(f"Encontrados {len(errors)} erros léxicos.")
        write_to_file(errors_output_file, errors)
    else:
        print("Nenhum erro léxico encontrado.")
        write_to_file(errors_output_file, [])

    print(f"Total de {len(tokens)} tokens reconhecidos.")
    write_to_file(tokens_output_file, tokens)


if __name__ == "__main__":
    main()

