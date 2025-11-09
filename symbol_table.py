class TableEntry(object):
    """
    Armazena as informações de uma entrada individual na tabela de símbolos.
    """

    def __init__(self, lexema: str, tipo: str, num_linha: int, kind: str):
        self.lexema = lexema  # Nome do identificador (ex: 'a')
        self.tipo = tipo  # Tipo do identificador (ex: 'int', 'float')
        self.num_linha = num_linha  # Linha onde foi declarado
        self.kind = kind  # Natureza do símbolo (ex: 'variable', 'parameter')

    def __repr__(self):
        """Retorna uma representação em string para facilitar a impressão."""
        return f"(Lexema: {self.lexema}, Tipo: {self.tipo}, Kind: {self.kind}, Linha: {self.num_linha})"


class SymbolTable:
    """
    Implementa a Tabela de Símbolos com uma pilha de escopos.
    Cada função terá seu próprio escopo.
    """

    def __init__(self):
        # A pilha de escopos. Cada item é um dicionário
        # que mapeia um 'lexema' (str) para um 'TableEntry'.
        self.scopes = [{}]

    def enter_scope(self):
        """ Cria um novo escopo (ao entrar em uma função). """
        self.scopes.append({})

    def exit_scope(self):
        """ Sai do escopo atual (ao sair de uma função). """
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            # Isso não deve acontecer se o parser estiver correto
            print("Erro: Tentando sair do escopo global.")

    def add_entry(self, entry: TableEntry):
        """
        Adiciona uma nova entrada (TableEntry) ao escopo ATUAL (o topo da pilha).
        """
        current_scope = self.scopes[-1]

        if entry.lexema in current_scope:
            pass

        current_scope[entry.lexema] = entry

    def lookup(self, lexema: str) -> TableEntry | None:
        """
        Procura um 'lexema' começando do escopo mais interno
        para o mais externo.
        """
        for scope in reversed(self.scopes):
            if lexema in scope:
                return scope[lexema]

        return None  # Não encontrado

    def get_current_scope(self) -> dict[str, TableEntry]:
        """
        Retorna o dicionário do escopo atual.
        Útil para o parser salvar a tabela final da função.
        """
        return self.scopes[-1]