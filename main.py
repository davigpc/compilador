import sys
from lexer import Lexer, Token

def write_to_file(filename: str, content: list):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
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

    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{source_file_path}' não foi encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        sys.exit(1)

    # Instanciar e executar o analisador léxico
    lexer = Lexer(source_code)
    tokens, errors = lexer.scan_tokens()

    # Escrever saídas
    if errors:
        print(f"Encontrados {len(errors)} erros léxicos.")
        write_to_file("lexical_errors.txt", errors)
    else:
        print("Nenhum erro léxico encontrado.")
        write_to_file("lexical_errors.txt", [])

    print(f"Total de {len(tokens)} tokens reconhecidos.")
    write_to_file("tokens.txt", tokens)

if __name__ == "__main__":
    main()