#!python
from typing import List,Dict

# = Internal Constants =======================
DEBUG_MODE   = False

TERMINAL     = True
NON_TERMINAL = False
START_TAG    = True
END_TAG      = False

FUNCTION     = 'function'
METHOD_OWN   = 'method_own'
METHOD_OTHER = 'method_other'

# = Jack Tokenizer ===========================
# Keyword constants
KW_CLASS        = 'class'
KW_METHOD       = 'method'
KW_FUNCTION     = 'function'
KW_CONSTRUCTOR  = 'constructor'
KW_INT          = 'int'
KW_BOOLEAN      = 'boolean'
KW_CHAR         = 'char'
KW_VOID         = 'void'
KW_VAR          = 'var'
KW_STATIC       = 'static'
KW_FIELD        = 'field'
KW_LET          = 'let'
KW_DO           = 'do'
KW_IF           = 'if'
KW_ELSE         = 'else'
KW_WHILE        = 'while'
KW_RETURN       = 'return'
KW_TRUE         = 'true'
KW_FALSE        = 'false'
KW_NULL         = 'null'
KW_THIS         = 'this'
KEYWORDS_LIST = [KW_CLASS, KW_METHOD, KW_FUNCTION, KW_CONSTRUCTOR, 
                 KW_INT, KW_BOOLEAN,KW_CHAR, KW_VOID, 
                 KW_VAR, KW_STATIC, KW_FIELD, 
                 KW_LET, KW_DO, KW_IF, KW_ELSE, KW_WHILE, KW_RETURN, 
                 KW_TRUE, KW_FALSE, KW_NULL, KW_THIS]

# Symbol constants
SYMBOLS_LIST = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

# Token tag constants
T_KEYWORD     = 'keyword'
T_SYMBOL      = 'symbol'
T_INT_CONST   = 'integerConstant'
T_STR_CONST   = 'stringConstant'
T_IDENTIFIER  = 'identifier'

# Symbol kinds
SK_STATIC   = "static"
SK_FIELD    = "field"
SK_ARG      = "arg"
SK_VAR      = "var"
SEGMENTS_DICT = {SK_STATIC:'static', SK_FIELD:'this', SK_ARG:'argument', SK_VAR:'local', None:'ERROR'} 

# operand list
OP_NEG = '-'
OP_NOT = '~'
OP_ADD = '+'
OP_SUB = '-'
OP_MUL = '*'
OP_DIV = '/'
OP_AND = '&'
OP_OR  = '|'
OP_LT  = '<'
OP_GT  = '>'
OP_EQ  = '='

# 単項演算子
UNARY_OP_DICT = {
    OP_NEG : 'neg',
    OP_NOT : 'not',
}

# ２項演算子
BIN_OP_DICT = {
    OP_ADD : 'add',
    OP_SUB : 'sub',
    OP_MUL : "call Math.multiply 2",
    OP_DIV : 'call Math.divide 2',
    OP_AND : 'and',
    OP_OR  : 'or',
    OP_LT  : 'lt',
    OP_GT  : 'gt',
    OP_EQ  : 'eq',
    OP_NOT : 'not',
}
