import sys
import os
import json
from dataclasses import asdict
from lexer import Lexer, Token
from parser import Parser
from symbol_table import TableEntry
import ast_nodes


def write_json(filename: str, data: dict):
    """Escreve dados (ASTs e Tabelas) em JSON formatado."""

    def serializer(obj):
        if isinstance(obj, TableEntry):
            return obj.__dict__

        # Se for um nó da ASA (dataclass), converte para dicionário
        if hasattr(obj, '__dataclass_fields__'):
            d = asdict(obj)
            # Campo extra para saber o tipo do nó
            d['_node_type'] = obj.__class__.__name__
            return d

        raise TypeError(f"Objeto {type(obj)} não serializável")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=serializer, indent=2, ensure_ascii=False)
        print(f"Arquivo gerado com sucesso: {filename}")
    except Exception as e:
        print(f"Erro ao salvar JSON {filename}: {e}")


def write_errors(filename: str, errors: list):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for err in errors:
                f.write(str(err) + '\n')
        print(f"Log de erros gerado: {filename}")
    except Exception as e:
        print(f"Erro ao salvar erros {filename}: {e}")


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

    # Nomes dos arquivos
    lexical_errors_file = os.path.join(ERROS_DIR, f"{base_name}_lexical_errors.txt")
    syntactic_errors_file = os.path.join(ERROS_DIR, f"{base_name}_syntactic_errors.txt")
    symbol_tables_file = os.path.join(SAIDAS_DIR, f"{base_name}_symbol_tables.json")
    ast_file = os.path.join(SAIDAS_DIR, f"{base_name}_ast.json")

    # 1. Leitura
    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)

    # 2. Análise Léxica
    print("--- Análise Léxica ---")
    lexer = Lexer(source_code)
    tokens, lexical_errors = lexer.scan_tokens()

    write_errors(lexical_errors_file, lexical_errors)

    if lexical_errors:
        print(f"Encontrados {len(lexical_errors)} erros léxicos. Parando.")
        sys.exit(1)
    else:
        print(f"Sucesso! {len(tokens)} tokens gerados.")

    # 3. Análise Sintática e Semântica (ASA)
    print("--- Análise Sintática e Semântica ---")
    parser = Parser(tokens)

    # O parser retorna ASAs
    syntactic_errors, function_tables, function_asts = parser.parse_program()

    write_errors(syntactic_errors_file, syntactic_errors)

    if syntactic_errors:
        print(f"Encontrados {len(syntactic_errors)} erros sintáticos/semânticos.")
    else:
        print("Sucesso! Nenhum erro sintático encontrado.")

    # 4. Escrever Saídas (JSON)
    write_json(symbol_tables_file, function_tables)
    write_json(ast_file, function_asts)

    print("Processo concluído.")


if __name__ == "__main__":
    main()