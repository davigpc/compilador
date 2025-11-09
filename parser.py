from lexer import Token, TokenType
from symbol_table import SymbolTable, TableEntry


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.symbol_table = SymbolTable()
        
        self.function_tables = {}

    def parse_program(self) -> tuple[list[str], dict]:
        """
        Ponto de entrada do parser.
        Regra: Programa -> Funcao FuncaoSeq
        Regra: FuncaoSeq -> Funcao FuncaoSeq | ε
        """
        while not self.is_at_end() and self.peek().token_type == TokenType.FUNCTION:
            try:
                self.parse_function()
            except Exception as e:
                self.errors.append(str(e))
                self.synchronize()

        if not self.is_at_end():
            self.errors.append(
                f"Erro Sintático: Esperado 'fn' ou fim de arquivo, mas encontrado {self.peek().lexeme} na linha {self.peek().line}.")

        return self.errors, self.function_tables

    def parse_function(self):
        """
        Regra: Funcao -> fn NomeFuncao (ListaParams) TipoRetornoFuncao Bloco
        """
        self.consume(TokenType.FUNCTION, "Esperado 'fn' para iniciar uma função.")

        # Regra: NomeFuncao -> ID | MAIN
        fun_token = self.peek()
        if fun_token.token_type not in [TokenType.ID, TokenType.MAIN]:
            raise Exception(f"Esperado nome de função (ID ou 'main'), mas encontrado {fun_token.lexeme}.")

        fun_name = self.advance().lexeme

        self.symbol_table.enter_scope()
        current_fun_table = self.symbol_table.get_current_scope()
        self.function_tables[fun_name] = current_fun_table

        self.consume(TokenType.LBRACKET, f"Esperado '(' após o nome da função '{fun_name}'.")

        # Regra: ListaParams -> ID: Type ListaParams2 | ε
        self.parse_lista_params()

        self.consume(TokenType.RBRACKET, f"Esperado ')' após a lista de parâmetros.")

        # Regra: TipoRetornoFuncao -> -> Type | ε
        if self.match(TokenType.ARROW):
            self.parse_type()

        # Regra: Bloco -> { Sequencia }
        self.parse_bloco()

        self.symbol_table.exit_scope()

    def parse_lista_params(self):
        """
        Regra: ListaParams -> ID: Type ListaParams2 | ε
        Regra: ListaParams2 -> , ID: Type ListaParams2 | ε
        """
        if self.peek().token_type == TokenType.ID:
            param_token = self.consume(TokenType.ID, "Esperado nome de parâmetro.")
            self.consume(TokenType.COLON, "Esperado ':' após nome de parâmetro.")
            param_type = self.parse_type()

            entry = TableEntry(param_token.lexeme, param_type, param_token.line, 'parameter')
            self.symbol_table.add_entry(entry)

            while self.match(TokenType.COMMA):
                param_token = self.consume(TokenType.ID, "Esperado nome de parâmetro após vírgula.")
                self.consume(TokenType.COLON, "Esperado ':' após nome de parâmetro.")
                param_type = self.parse_type()

                entry = TableEntry(param_token.lexeme, param_type, param_token.line, 'parameter')
                self.symbol_table.add_entry(entry)

    def parse_type(self) -> str:
        """
        Regra: Type -> int | float | char
        """
        if self.match(TokenType.INT):
            return 'int'
        elif self.match(TokenType.FLOAT):
            return 'float'
        elif self.match(TokenType.CHAR):
            return 'char'
        else:
            raise Exception(f"Esperado um tipo (int, float, char), mas encontrado {self.peek().lexeme}.")

    def parse_bloco(self):
        """
        Regra: Bloco -> { Sequencia }
        """
        self.consume(TokenType.LBRACE, "Esperado '{' para iniciar um bloco.")

        # Regra: Sequencia -> ... | ε
        self.parse_sequencia()

        self.consume(TokenType.RBRACE, "Esperado '}' para fechar um bloco.")

    def parse_sequencia(self):
        """
        Regra: Sequencia -> Declaracao Sequencia | Comando Sequencia | ε
        """
        
        while self.peek().token_type != TokenType.RBRACE and not self.is_at_end():
            if self.peek().token_type == TokenType.LET:
                self.parse_declaracao()
            else:
                self.parse_comando()

    def parse_declaracao(self):
        """
        Regra: Declaracao -> let VarList: Type;
        Regra: VarList -> ID VarList2
        """
        self.consume(TokenType.LET, "Esperado 'let'.")

        var_tokens = []  

        var_tokens.append(self.consume(TokenType.ID, "Esperado identificador (nome de variável)."))
        while self.match(TokenType.COMMA):
            var_tokens.append(self.consume(TokenType.ID, "Esperado identificador após vírgula."))

        self.consume(TokenType.COLON, "Esperado ':' após lista de variáveis.")
        var_type = self.parse_type()
        self.consume(TokenType.SEMICOLON, "Esperado ';' após declaração de variável.")

        for var_token in var_tokens:
            entry = TableEntry(var_token.lexeme, var_type, var_token.line, 'variable')
            self.symbol_table.add_entry(entry)

    def parse_comando(self):
        """
        Regra: Comando -> ID AtribuicaoOuChamada | ComandoSe | ...
        """
        token_type = self.peek().token_type

        if token_type == TokenType.ID:
            self.advance()  # Consome o ID
            self.parse_atribuicao_ou_chamada()
        elif token_type == TokenType.IF:
            self.parse_comando_se()
        elif token_type == TokenType.WHILE:
            self.parse_while()
        elif token_type == TokenType.PRINTLN:
            self.parse_println()
        elif token_type == TokenType.RETURN:
            self.parse_return()
        else:
            raise Exception(f"Comando inválido. Encontrado token inesperado '{self.peek().lexeme}'.")

    def parse_atribuicao_ou_chamada(self):
        """
        Regra: AtribuicaoOuChamada -> = Expr; | (ListaArgs);
        (Chamado APÓS o ID ter sido consumido)
        """
        if self.match(TokenType.ASSIGN):  # Atribuição
            self.parse_expr()
            self.consume(TokenType.SEMICOLON, "Esperado ';' após expressão em uma atribuição.")
        elif self.match(TokenType.LBRACKET):  # Chamada de Função
            self.parse_lista_args()
            self.consume(TokenType.RBRACKET, "Esperado ')' após argumentos da função.")
            self.consume(TokenType.SEMICOLON, "Esperado ';' após chamada de função.")
        else:
            raise Exception("Esperado '=' (atribuição) ou '(' (chamada de função) após o ID.")

    def parse_comando_se(self):
        """
        Regra: ComandoSe -> if Expr Bloco ComandoSenao
        """
        self.consume(TokenType.IF, "Esperado 'if'.")
        self.parse_expr()
        self.parse_bloco()
        self.parse_comando_senao()

    def parse_comando_senao(self):
        """
        Regra: ComandoSenao -> else ComandoSe | else Bloco | ε
        """
        if self.match(TokenType.ELSE):
            if self.peek().token_type == TokenType.IF:
                self.parse_comando_se()  # else if...
            else:
                self.parse_bloco()  # else { ... }

    def parse_while(self):
        """
        Regra: while Expr Bloco
        """
        self.consume(TokenType.WHILE, "Esperado 'while'.")
        self.parse_expr()
        self.parse_bloco()

    def parse_println(self):
        """
        Regra: println(FMT_STRING, ListaArgs);
        """
        self.consume(TokenType.PRINTLN, "Esperado 'println'.")
        self.consume(TokenType.LBRACKET, "Esperado '(' após 'println'.")
        self.consume(TokenType.FMT_STRING, "Esperado string de formatação.")

        if self.match(TokenType.COMMA):
            self.parse_lista_args()

        self.consume(TokenType.RBRACKET, "Esperado ')' após argumentos do 'println'.")
        self.consume(TokenType.SEMICOLON, "Esperado ';' após comando 'println'.")

    def parse_return(self):
        """
        Regra: return Expr;
        """
        self.consume(TokenType.RETURN, "Esperado 'return'.")
        self.parse_expr()
        self.consume(TokenType.SEMICOLON, "Esperado ';' após expressão de 'return'.")

    def parse_expr(self):
        """ Regra: Expr -> Rel ExprOpc (Op: ==, !=) """
        self.parse_rel()
        while self.peek().token_type in [TokenType.EQ, TokenType.NE]:
            self.advance()  # Consome o '==' ou '!='
            self.parse_rel()

    def parse_rel(self):
        """ Regra: Rel -> Adicao RelOpc (Op: <, <=, >, >=) """
        self.parse_adicao()
        while self.peek().token_type in [TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE]:
            self.advance()  # Consome o operador relacional
            self.parse_adicao()

    def parse_adicao(self):
        """ Regra: Adicao -> Termo AdicaoOpc (Op: +, -) """
        self.parse_termo()
        while self.peek().token_type in [TokenType.PLUS, TokenType.MINUS]:
            self.advance()  # Consome o '+' ou '-'
            self.parse_termo()

    def parse_termo(self):
        """ Regra: Termo -> Fator TermoOpc (Op: *, /) """
        self.parse_fator()
        while self.peek().token_type in [TokenType.MULT, TokenType.DIV]:
            self.advance()  # Consome o '*' ou '/'
            self.parse_fator()

    def parse_fator(self):
        """
        Regra: Fator -> ID ChamadaFuncao | INT_CONST | FLOAT_CONST |
                        CHAR_LITERAL | (Expr)
        """
        if self.peek().token_type == TokenType.ID:
            self.advance()  # Consome ID
            self.parse_chamada_funcao()  # Regra: ChamadaFuncao -> (ListaArgs) | ε
        elif self.match(TokenType.INT_CONST):
            pass
        elif self.match(TokenType.FLOAT_CONST):
            pass
        elif self.match(TokenType.CHAR_LITERAL):
            pass
        elif self.match(TokenType.LBRACKET):
            self.parse_expr()
            self.consume(TokenType.RBRACKET, "Esperado ')' após expressão entre parênteses.")
        else:
            raise Exception(f"Fator inesperado: {self.peek().lexeme}.")

    def parse_chamada_funcao(self):
        """
        Regra: ChamadaFuncao -> (ListaArgs) | ε
        (Chamado APÓS o ID ter sido consumido)
        """
        if self.match(TokenType.LBRACKET):
            self.parse_lista_args()
            self.consume(TokenType.RBRACKET, "Esperado ')' após lista de argumentos.")

    def parse_lista_args(self):
        """
        Regra: ListaArgs -> Arg ListaArgs2 | ε
        Regra: ListaArgs2 -> , Arg ListaArgs2 | ε
        """
        if self.peek().token_type != TokenType.RBRACKET:
            self.parse_arg()
            while self.match(TokenType.COMMA):
                self.parse_arg()

    def parse_arg(self):
        """
        Regra: Arg -> ID ChamadaFuncao | INT_CONST | FLOAT_CONST | CHAR_LITERAL
        """
        if self.peek().token_type == TokenType.ID:
            self.advance()  # Consome ID
            self.parse_chamada_funcao()
        elif self.match(TokenType.INT_CONST):
            pass
        elif self.match(TokenType.FLOAT_CONST):
            pass
        elif self.match(TokenType.CHAR_LITERAL):
            pass
        else:
            raise Exception(f"Argumento inválido: {self.peek().lexeme}.")

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def match(self, token_type: TokenType) -> bool:
        """
        Verifica se o token atual é do tipo esperado.
        Se sim, consome e retorna True. Senão, retorna False.
        """
        if self.is_at_end():
            return False
        if self.peek().token_type == token_type:
            self.advance()
            return True
        return False

    def consume(self, token_type: TokenType, error_message: str) -> Token:
        """
        Exige que o token atual seja do tipo esperado.
        Se for, consome. Se não for, lança uma exceção.
        """
        if self.peek().token_type == token_type:
            return self.advance()

        # Erro Sintático
        raise Exception(
            f"Erro Sintático na linha {self.peek().line}: {error_message} (Encontrado '{self.peek().lexeme}')")

    def synchronize(self):

        while not self.is_at_end():
            token_type = self.peek().token_type

            # Ponto de sincronização: ponto e vírgula
            if token_type == TokenType.SEMICOLON:
                self.advance()
                return

            # Ponto de sincronização: início de palavras-chave
            if token_type in [
                TokenType.FUNCTION,
                TokenType.LET,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.RETURN,
                TokenType.RBRACE  # Fim de um bloco
            ]:
                return

            self.advance()
