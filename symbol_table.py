class TableEntry(object):

    def __init__(self, lexema: str, tipo: str, num_linha: int, kind: str):
        self.lexema = lexema
        self.tipo = tipo
        self.num_linha = num_linha
        self.kind = kind

    def __repr__(self):
        # Simplificado para o JSON ficar limpo
        return f"{{lexema: {self.lexema}, tipo: {self.tipo}, kind: {self.kind}, linha: {self.num_linha}}}"


class SymbolTable:

    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            print("Erro: Tentando sair do escopo global.")

    def add_entry(self, entry: TableEntry):
        current_scope = self.scopes[-1]

        # --- Regra de Variável Redeclarada ---
        if entry.lexema in current_scope:
            raise Exception(
                f"Erro Semântico na linha {entry.num_linha}: O identificador '{entry.lexema}' já foi declarado neste escopo.")

        current_scope[entry.lexema] = entry

    def lookup(self, lexema: str) -> TableEntry | None:
        for scope in reversed(self.scopes):
            if lexema in scope:
                return scope[lexema]

        return None

    def get_current_scope(self) -> dict[str, TableEntry]:
        return self.scopes[-1]