import sys
import os
import json 
from lexer import Lexer, Token
from parser import Parser
from symbol_table import TableEntry


def write_to_file(filename: str, content: list):
    """Escreve o conteúdo de uma lista (erros) em um arquivo, um item por linha."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if not content:
                f.write("")  
            else:
                for item in content:
                    f.write(str(item) + '\n')
        print(f"Saída de erros escrita com sucesso em '{filename}'.")
    except IOError as e:
        print(f"Erro ao escrever no arquivo '{filename}': {e}")


def write_symbol_tables_to_json(filename: str, tables: dict):

    def default_serializer(obj):
        """
        Converte objetos (como TableEntry) em um dicionário
        para que o JSON saiba como salvá-los.
        """
        if isinstance(obj, TableEntry):
            return obj.__dict__
        raise TypeError(f"Objeto do tipo {obj.__class__.__name__} não é serializável por JSON")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Usa o 'default_serializer' para lidar com seus objetos TableEntry
            json.dump(tables, f, default=default_serializer, indent=4, ensure_ascii=False)
        print(f"Tabelas de símbolos escritas com sucesso em '{filename}'.")
    except IOError as e:
        print(f"Erro ao escrever tabelas de símbolos JSON em '{filename}': {e}")
    except TypeError as e:
        print(f"Erro ao serializar tabelas de símbolos: {e}")


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <caminho_para_arquivo_fonte>")
        sys.exit(1)

    source_file_path = sys.argv[1]

    SAIDAS_DIR = "saidas"
    ERROS_DIR = "erros"

    os.makedirs(SAIDAS_DIR, exist_ok=True)
    os.makedirs(ERROS_DIR, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(source_file_path))[0]

    tokens_output_file = os.path.join(SAIDAS_DIR, f"{base_name}_tokens.txt")  
    lexical_errors_file = os.path.join(ERROS_DIR, f"{base_name}_lexical_errors.txt")

    syntactic_errors_file = os.path.join(ERROS_DIR, f"{base_name}_syntactic_errors.txt")
    symbol_tables_file = os.path.join(SAIDAS_DIR, f"{base_name}_symbol_tables.json") 

    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{source_file_path}' não foi encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        sys.exit(1)

    print("Iniciando análise léxica...")
    lexer = Lexer(source_code)
    tokens, lexical_errors = lexer.scan_tokens()

    write_to_file(lexical_errors_file, lexical_errors)

    if lexical_errors:
        print(f"Encontrados {len(lexical_errors)} erros léxicos. A compilação foi interrompida.")
        sys.exit(1)
    else:
        print("Nenhum erro léxico encontrado.")
        write_to_file(tokens_output_file, tokens)
        print(f"Total de {len(tokens)} tokens reconhecidos.")

    print("Iniciando análise sintática...")
    parser = Parser(tokens)
    syntactic_errors, function_tables = parser.parse_program()

    write_to_file(syntactic_errors_file, syntactic_errors)
    if syntactic_errors:
        print(f"Encontrados {len(syntactic_errors)} erros sintáticos.")
    else:
        print("Nenhum erro sintático encontrado.")

    write_symbol_tables_to_json(symbol_tables_file, function_tables)


if __name__ == "__main__":
    main()
