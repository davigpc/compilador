import re
from enum import Enum, auto
from dataclasses import dataclass

# Definição dos Tipos de Token
class TokenType(Enum):
    # Palavras Reservadas
    FUNCTION = auto()
    MAIN = auto()
    LET = auto()
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINTLN = auto()
    RETURN = auto()

    # Identificador e Constantes
    ID = auto()
    INT_CONST = auto()
    FLOAT_CONST = auto()
    CHAR_LITERAL = auto()
    FMT_STRING = auto()

    # Sinais e Operadores
    LBRACKET = auto()     # (
    RBRACKET = auto()     # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    ARROW = auto()        # ->
    COLON = auto()        # :
    SEMICOLON = auto()    # ;
    COMMA = auto()        # ,
    ASSIGN = auto()       # =
    EQ = auto()           # ==
    NE = auto()           # !=
    GT = auto()           # >
    GE = auto()           # >=
    LT = auto()           # <
    LE = auto()           # <=
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULT = auto()         # *
    DIV = auto()          # /

# Estrutura do Token
@dataclass
class Token:
    lexeme: str
    token_type: TokenType
    line: int

    def __str__(self):
        return f"Token(Lexema: '{self.lexeme}', Tipo: {self.token_type.name}, Linha: {self.line})"

# Analisador Léxico
class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.line = 1
        self.position = 0
        self.tokens = []
        self.errors = []

        self.token_specs = [
            # Ignorar espaços em branco e comentários
            ('SKIP', r'[ \t\r\f\v]+'),
            ('NEWLINE', r'\n'),
            
            # Comentários
            ('COMMENT', r'//.*'),

            # Palavras Reservadas
            ('FUNCTION', r'\bfn\b'),
            ('MAIN', r'\bmain\b'),
            ('LET', r'\blet\b'),
            ('INT', r'\bint\b'),
            ('FLOAT', r'\bfloat\b'),
            ('CHAR', r'\bchar\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('WHILE', r'\bwhile\b'),
            ('PRINTLN', r'\bprintln\b'),
            ('RETURN', r'\breturn\b'),
            
            # Constantes e Literais
            ('FLOAT_CONST', r'[0-9]+\.[0-9]+'),
            ('INT_CONST', r'[0-9]+'),
            ('FMT_STRING', r'"[^"]*"'), 
            ('CHAR_LITERAL', r"'([^'\\]|\\.)'"), # Aceita caracteres escapados como '\''

            # Identificador
            ('ID', r'[a-zA-Z][a-zA-Z0-9_]*'),

            # Operadores e Pontuação
            ('ARROW', r'->'),
            ('EQ', r'=='),
            ('NE', r'!='),
            ('GE', r'>='),
            ('LE', r'<='),
            ('ASSIGN', r'='),
            ('GT', r'>'),
            ('LT', r'<'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULT', r'\*'),
            ('DIV', r'/'),
            ('LBRACKET', r'\('),
            ('RBRACKET', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('COLON', r':'),
            ('SEMICOLON', r';'),
            ('COMMA', r','),

            # Erro
            ('MISMATCH', r'.'),
        ]
        self.tokenizer_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in self.token_specs))

    def scan_tokens(self) -> tuple[list[Token], list[str]]:
        while self.position < len(self.source):
            match = self.tokenizer_regex.match(self.source, self.position)
            
            if not match:
                self.errors.append(f"Erro léxico inesperado na linha {self.line}.")
                self.position += 1
                continue

            kind = match.lastgroup
            value = match.group()
            self.position = match.end()

            if kind == 'SKIP' or kind == 'COMMENT':
                continue
            elif kind == 'NEWLINE':
                self.line += 1
            elif kind == 'MISMATCH':
                self.errors.append(f"Erro Léxico: Caractere inesperado '{value}' na linha {self.line}.")
            else:
                token_type = TokenType[kind]
                self.tokens.append(Token(value, token_type, self.line))

        return self.tokens, self.errors