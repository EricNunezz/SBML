#Eric Nunez
#Student ID: 114806268

import ply.lex as lex
import ply.yacc as yacc
import re

from sbml_ast import (
    NumberNode, BooleanNode, StringNode,
    ListNode, TupleNode, BinaryOpNode,
    UnaryOpNode, IndexNode, TupleIndexNode
)

tokens = ('NUMBER', 'BOOLEAN','STRING',
          'PLUS', 'MINUS', 'TIMES','DIVIDE','POWER','DIV', 'MOD', 'CONS',
          'LT', 'LE', 'EQ', 'NE', 'GE', 'GT',
          'NOT','ANDALSO','ORELSE',
          'IN',
          'HASH','LPAREN','RPAREN','LBRACKET','RBRACKET','COMMA',

          'ID', 'LBRACE', 'RBRACE', 'SEMI', 'ASSIGN',
          'PRINT', 'IF', 'ELSE', 'WHILE'
          )

def t_error(t):
    t.lexer.skip(1)
    raise SyntaxError("SYNTAX ERROR")

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_PLUS = r'\+'
t_MINUS = r'-'
t_POWER = r'\*\*'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_CONS = r'::'

t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_EQ = r'=='
t_NE = r'<>|!='
t_GT = r'>'
t_HASH = r'\#'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_ASSIGN = r'='
t_ignore = ' \t'

def t_NUMBER(t):
    r'((\d+\.\d*)|(\.\d+)|(\d+))([eE][+-]?\d+)?'
    text = t.value
    if re.search(r'[\.eE]', text):
        t.value = float(text)
    else:
        t.value = int(text)
    return t

def t_BOOLEAN(t):
    r'True|False'
    t.value = True if t.value == "True" else False
    return t

def t_STRING(t):
    r'(\"([^\\"]|\\.)*\")|(\'([^\\\']|\\.)*\')'
    t.value = t.value[1:-1]
    return t

def t_DIV(t):
    r'div'
    return t

def t_MOD(t):
    r'mod'
    return t

def t_NOT(t):
    r'not'
    return t

def t_ANDALSO(t):
    r'andalso'
    return t

def t_ORELSE(t):
    r'orelse'
    return t

def t_IN(t):
    r'in'
    return t

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
}

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

precedence = (
    ('left', 'ORELSE'),
    ('left', 'ANDALSO'),
    ('right', 'NOT'),
    ('left', 'LT', 'LE', 'EQ', 'NE', 'GE', 'GT'),
    ('right', 'CONS'),
    ('left', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left','TIMES', 'DIVIDE', 'DIV', 'MOD'),
    ('right', 'POWER'),
    ('right', 'UMINUS')
)

#------------ Parser Section------------

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = NumberNode(p[1])

def p_expression_boolean(p):
    'expression : BOOLEAN'
    p[0] = BooleanNode(p[1])

def p_expression_string(p):
    'expression : STRING'
    p[0] = StringNode(p[1])

def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression DIV expression
               | expression MOD expression
               | expression POWER expression
               | expression ANDALSO expression
               | expression ORELSE expression
               | expression LT expression
               | expression LE expression
               | expression EQ expression
               | expression NE expression
               | expression GE expression
               | expression GT expression
               | expression CONS expression
               | expression IN expression
    '''
    p[0] = BinaryOpNode(p[2], p[1], p[3])


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    if p is None:
        print("Syntax Error at EQF")
    else:
        print(f"SYntax Error at token {p.type}, value = {p.value!r}")
    raise SyntaxError("SYNtax ERROR")

def p_expression_not(p):
    'expression : NOT expression'
    p[0] = UnaryOpNode('not', p[2])

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = UnaryOpNode('-', p[2])

def p_expression_uplus(p):
    'expression : PLUS expression'
    p[0] = UnaryOpNode('+', p[2])




#------List Grammar rules------
def p_expression_list_empty(p):
    'expression : LBRACKET RBRACKET'
    p[0] = ListNode([])

def p_expression_list_nonempty(p):
    'expression : LBRACKET l_items RBRACKET'
    p[0] = ListNode(p[2])

def p_l_items_single(p):
    'l_items : expression'
    p[0] = [p[1]]
def p_l_items_more(p):
    'l_items : l_items COMMA expression'
    p[0] = p[1] + [p[3]]

#------Tuple Grammar rules------
def p_expression_tuple_single(p):
    'expression : LPAREN expression COMMA RPAREN'
    p[0] = TupleNode([p[2]])

def p_expression_tuple_multi(p):
    'expression : LPAREN t_items RPAREN'
    p[0] = TupleNode(p[2])

def p_t_items_one(p):
    't_items : expression'
    p[0] = [p[1]]

def p_t_items_more(p):
    't_items : expression COMMA t_items'
    p[0] = [p[1]] + p[3]

#----- Indexing Grammar Rules-----
def p_expression_list_index(p):
    'expression : expression LBRACKET expression RBRACKET'
    p[0] = IndexNode(p[1], p[3])


def p_expression_tuple_index_multi(p):
    'expression : HASH NUMBER LPAREN t_items RPAREN'
    index_node = NumberNode(p[2])
    tuple_node = TupleNode(p[4])
    p[0] = TupleIndexNode(index_node, tuple_node)

def p_expression_tuple_index_single(p):
    'expression : HASH NUMBER LPAREN expression COMMA RPAREN'
    index_node = NumberNode(p[2])
    tuple_node = TupleNode([p[4]])
    p[0] = TupleIndexNode(index_node, tuple_node)

lexer = lex.lex()
parser = yacc.yacc()

#if __name__ == "__main__":
#    data = open("lexer_test").read()
#    lex = lexer  # already built by PLY at the end of your file
#    lex.input(data)
#    try:
#        while True:
#            tok = lex.token()
#            if not tok: break
#            print(tok.type, repr(tok.value))
#    except SyntaxError:
#        print("SYNTAX ERROR")