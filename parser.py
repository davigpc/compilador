from lexer import Token, TokenType
from symbol_table import SymbolTable, TableEntry
import ast_nodes as ast


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.symbol_table = SymbolTable()

        # Guardar resultados
        self.function_tables = {}
        self.function_asts = {}  # Guardar as ASTs

    # --- Utilitários ---
    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def match(self, token_type: TokenType) -> bool:
        if not self.is_at_end() and self.peek().token_type == token_type:
            self.advance()
            return True
        return False

    def consume(self, token_type: TokenType, msg: str) -> Token:
        if self.peek().token_type == token_type:
            return self.advance()
        raise Exception(f"Erro Sintático na linha {self.peek().line}: {msg} (Encontrado '{self.peek().lexeme}')")

    def synchronize(self):
        while not self.is_at_end():
            if self.peek().token_type == TokenType.SEMICOLON:
                self.advance()
                return
            if self.peek().token_type in [TokenType.FUNCTION, TokenType.LET, TokenType.IF, TokenType.WHILE,
                                          TokenType.RETURN, TokenType.RBRACE]:
                return
            self.advance()

    # --- Parsing ---

    def parse_program(self):
        while not self.is_at_end() and self.peek().token_type == TokenType.FUNCTION:
            try:
                func_node = self.parse_function()
                if func_node:
                    self.function_asts[func_node.name] = func_node
            except Exception as e:
                self.errors.append(str(e))
                self.synchronize()

        if not self.is_at_end():
            self.errors.append(f"Erro Sintático: Token inesperado '{self.peek().lexeme}' na linha {self.peek().line}.")

        return self.errors, self.function_tables, self.function_asts

    def parse_function(self) -> ast.FunctionDecl:
        self.consume(TokenType.FUNCTION, "Esperado 'fn'")

        name_tok = self.peek()
        if name_tok.token_type in [TokenType.ID, TokenType.MAIN]:
            self.advance()
            func_name = name_tok.lexeme
        else:
            raise Exception(f"Esperado nome de função na linha {name_tok.line}")

        entry = TableEntry(func_name, 'void', name_tok.line, 'function')
        self.symbol_table.add_entry(entry)

        self.symbol_table.enter_scope()
        self.function_tables[func_name] = self.symbol_table.get_current_scope()

        self.consume(TokenType.LBRACKET, "Esperado '('")
        params = self.parse_lista_params()
        self.consume(TokenType.RBRACKET, "Esperado ')'")

        return_type = 'void'
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()
            entry.tipo = return_type

        self.consume(TokenType.LBRACE, "Esperado '{'")
        body = self.parse_bloco()
        self.consume(TokenType.RBRACE, "Esperado '}'")

        self.symbol_table.exit_scope()

        return ast.FunctionDecl(name=func_name, params=params, return_type=return_type, body=body)

    def parse_lista_params(self) -> list[ast.Param]:
        params = []
        if self.peek().token_type == TokenType.ID:
            params.append(self._parse_single_param())
            while self.match(TokenType.COMMA):
                params.append(self._parse_single_param())
        return params

    def _parse_single_param(self) -> ast.Param:
        name_tok = self.consume(TokenType.ID, "Esperado ID")
        self.consume(TokenType.COLON, "Esperado ':'")
        ptype = self.parse_type()

        self.symbol_table.add_entry(TableEntry(name_tok.lexeme, ptype, name_tok.line, 'parameter'))
        return ast.Param(name=name_tok.lexeme, type=ptype)

    def parse_type(self) -> str:
        if self.match(TokenType.INT): return 'int'
        if self.match(TokenType.FLOAT): return 'float'
        if self.match(TokenType.CHAR): return 'char'
        raise Exception(f"Tipo inválido na linha {self.peek().line}")

    def parse_bloco(self) -> ast.Block:
        stmts = []
        while not self.is_at_end() and self.peek().token_type != TokenType.RBRACE:
            if self.peek().token_type == TokenType.LET:
                stmts.append(self.parse_declaracao())
            else:
                stmts.append(self.parse_comando())
        return ast.Block(statements=stmts)

    def parse_declaracao(self) -> ast.VarDecl:
        self.consume(TokenType.LET, "Esperado 'let'")
        names = []

        names.append(self.consume(TokenType.ID, "Esperado ID"))
        while self.match(TokenType.COMMA):
            names.append(self.consume(TokenType.ID, "Esperado ID"))

        self.consume(TokenType.COLON, "Esperado ':'")
        vtype = self.parse_type()
        self.consume(TokenType.SEMICOLON, "Esperado ';'")

        names_str = []
        for tok in names:
            self.symbol_table.add_entry(TableEntry(tok.lexeme, vtype, tok.line, 'variable'))
            names_str.append(tok.lexeme)

        return ast.VarDecl(names=names_str, type=vtype)

    def parse_comando(self) -> ast.AstNode:
        tt = self.peek().token_type

        if tt == TokenType.ID:
            return self.parse_atribuicao_ou_chamada()
        elif tt == TokenType.IF:
            return self.parse_if()
        elif tt == TokenType.WHILE:
            return self.parse_while()
        elif tt == TokenType.PRINTLN:
            return self.parse_println()
        elif tt == TokenType.RETURN:
            return self.parse_return()
        elif tt == TokenType.LBRACE:
            self.advance()
            blk = self.parse_bloco()
            self.consume(TokenType.RBRACE, "Esperado '}'")
            return blk
        else:
            raise Exception(f"Comando inválido '{self.peek().lexeme}' na linha {self.peek().line}")

    def parse_atribuicao_ou_chamada(self):
        id_tok = self.advance()

        # --- VERIFICAÇÃO SEMÂNTICA: Variável Não Declarada ---
        if not self.symbol_table.lookup(id_tok.lexeme):
            raise Exception(f"Erro Semântico na linha {id_tok.line}: Identificador '{id_tok.lexeme}' não declarado.")

        if self.match(TokenType.ASSIGN):
            val = self.parse_expr()
            self.consume(TokenType.SEMICOLON, "Esperado ';'")
            return ast.Assign(name=id_tok.lexeme, value=val)

        elif self.match(TokenType.LBRACKET):
            args = self.parse_lista_args()
            self.consume(TokenType.RBRACKET, "Esperado ')'")
            self.consume(TokenType.SEMICOLON, "Esperado ';'")
            return ast.FunctionCall(name=id_tok.lexeme, args=args)

        else:
            raise Exception(f"Esperado '=' ou '(' após ID na linha {id_tok.line}")

    def parse_if(self) -> ast.IfStmt:
        self.consume(TokenType.IF, "Esperado 'if'")
        cond = self.parse_expr()

        self.consume(TokenType.LBRACE, "Esperado '{'")
        then_b = self.parse_bloco()
        self.consume(TokenType.RBRACE, "Esperado '}'")

        else_b = None
        if self.match(TokenType.ELSE):
            if self.peek().token_type == TokenType.IF:
                else_b = self.parse_if()
            else:
                self.consume(TokenType.LBRACE, "Esperado '{'")
                else_b = self.parse_bloco()
                self.consume(TokenType.RBRACE, "Esperado '}'")

        return ast.IfStmt(condition=cond, then_branch=then_b, else_branch=else_b)

    def parse_while(self) -> ast.WhileStmt:
        self.consume(TokenType.WHILE, "Esperado 'while'")
        cond = self.parse_expr()
        self.consume(TokenType.LBRACE, "Esperado '{'")
        body = self.parse_bloco()
        self.consume(TokenType.RBRACE, "Esperado '}'")
        return ast.WhileStmt(condition=cond, body=body)

    def parse_println(self) -> ast.PrintlnStmt:
        self.consume(TokenType.PRINTLN, "Esperado 'println'")
        self.consume(TokenType.LBRACKET, "Esperado '('")
        fmt = self.consume(TokenType.FMT_STRING, "Esperado string").lexeme
        args = []
        if self.match(TokenType.COMMA):
            args = self.parse_lista_args()
        self.consume(TokenType.RBRACKET, "Esperado ')'")
        self.consume(TokenType.SEMICOLON, "Esperado ';'")
        return ast.PrintlnStmt(fmt_string=fmt, args=args)

    def parse_return(self) -> ast.ReturnStmt:
        self.consume(TokenType.RETURN, "Esperado 'return'")
        val = self.parse_expr()
        self.consume(TokenType.SEMICOLON, "Esperado ';'")
        return ast.ReturnStmt(value=val)

    def parse_expr(self) -> ast.AstNode:
        return self.parse_rel()

    def parse_rel(self) -> ast.AstNode:
        node = self.parse_adicao()
        while self.peek().token_type in [TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE, TokenType.EQ,
                                         TokenType.NE]:
            op = self.advance().lexeme
            right = self.parse_adicao()
            node = ast.BinOp(left=node, op=op, right=right)
        return node

    def parse_adicao(self) -> ast.AstNode:
        node = self.parse_termo()
        while self.peek().token_type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.advance().lexeme
            right = self.parse_termo()
            node = ast.BinOp(left=node, op=op, right=right)
        return node

    def parse_termo(self) -> ast.AstNode:
        node = self.parse_fator()
        while self.peek().token_type in [TokenType.MULT, TokenType.DIV]:
            op = self.advance().lexeme
            right = self.parse_fator()
            node = ast.BinOp(left=node, op=op, right=right)
        return node

    def parse_fator(self) -> ast.AstNode:
        tok = self.peek()

        if tok.token_type == TokenType.ID:
            self.advance()

            if not self.symbol_table.lookup(tok.lexeme):
                raise Exception(f"Erro Semântico na linha {tok.line}: Identificador '{tok.lexeme}' não declarado.")

            if self.match(TokenType.LBRACKET):
                args = self.parse_lista_args()
                self.consume(TokenType.RBRACKET, "Esperado ')'")
                return ast.FunctionCall(name=tok.lexeme, args=args)
            return ast.VarAccess(name=tok.lexeme)

        elif tok.token_type == TokenType.INT_CONST:
            self.advance()
            return ast.Literal(value=int(tok.lexeme), type='int')
        elif tok.token_type == TokenType.FLOAT_CONST:
            self.advance()
            return ast.Literal(value=float(tok.lexeme), type='float')
        elif tok.token_type == TokenType.CHAR_LITERAL:
            self.advance()
            return ast.Literal(value=tok.lexeme, type='char')

        elif self.match(TokenType.LBRACKET):
            expr = self.parse_expr()
            self.consume(TokenType.RBRACKET, "Esperado ')'")
            return expr

        raise Exception(f"Fator inesperado '{tok.lexeme}' na linha {tok.line}")

    def parse_lista_args(self) -> list[ast.AstNode]:
        args = []
        if self.peek().token_type != TokenType.RBRACKET:
            args.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expr())
        return args