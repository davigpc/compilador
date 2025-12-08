# Arquivo: ast_nodes.py
from dataclasses import dataclass
from typing import List, Optional, Union

# Classe Base
@dataclass
class AstNode:
    pass

# --- Estruturas Principais ---

@dataclass
class Program(AstNode):
    functions: List['FunctionDecl']

@dataclass
class FunctionDecl(AstNode):
    name: str
    params: List['Param']
    return_type: str
    body: 'Block'

@dataclass
class Param(AstNode):
    name: str
    type: str

@dataclass
class Block(AstNode):
    statements: List[AstNode]

# --- Comandos ---

@dataclass
class VarDecl(AstNode):
    names: List[str]
    type: str

@dataclass
class Assign(AstNode): # Corresponde ao 'Attr' do PDF
    name: str
    value: AstNode

@dataclass
class IfStmt(AstNode):
    condition: AstNode
    then_branch: 'Block'
    else_branch: Optional[Union['Block', 'IfStmt']] = None

@dataclass
class WhileStmt(AstNode):
    condition: AstNode
    body: 'Block'

@dataclass
class PrintlnStmt(AstNode):
    fmt_string: str
    args: List[AstNode]

@dataclass
class ReturnStmt(AstNode):
    value: AstNode

# --- Expressões ---

@dataclass
class BinOp(AstNode): # Aritmética, Relacional, Lógica
    left: AstNode
    op: str
    right: AstNode

@dataclass
class Literal(AstNode): # Num, Char
    value: Union[int, float, str]
    type: str

@dataclass
class VarAccess(AstNode): # Id (uso)
    name: str

@dataclass
class FunctionCall(AstNode):
    name: str
    args: List[AstNode]