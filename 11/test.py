#!python
import sys,os,html
from collections import deque
from typing import List,Dict

# Symbol kinds
SK_STATIC   = 0
SK_FIELD    = 1
SK_ARG      = 2
SK_VAR      = 3
SK_NONE     = 4

class Main(object):
    st=SymbolTable()
    st.define('x', 'int', SK_STATIC)


class SymbolTable(object):
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.symbols = {SK_STATIC: self.class_symbols
                      , SK_FIELD : self.class_symbols
                      , SK_ARG   : self.subroutine_symbols
                      , SK_VAR   : self.subroutine_symbols
                      }
        self.index = {SK_STATIC:0, SK_FIELD:0, SK_ARG:0, SK_VAR:0}

    def __str__(self):
        return self.symbol_string('class', self.class_symbols)    \
             + self.symbol_string('subroutine', self.subroutine_symbols)
        
    def symbol_string(self, name, table):
        result = 'symbol table '+name+':\n'
        for n, (t, k, i) in table.items():
            result += 'symbol name:'+n+', type:'+t+', kind:'+k+', index:'+str(i)+'\n'
        return result
    
    def start_subroutine(self):
        self.subroutine_symbols.clear()
        self.index[SK_ARG] = 0
        self.index[SK_VAR] = 0
    
    def define(self, name, type, kind):
        '''
        与えられた名前、型、属性を持つ新しい識別子を定義し、インデックスを割り当てる。
        STATIC,FIELD 識別子にはクラススコープに割り当て、ARG,VAR 識別子はサブルーチンスコープに割り当てる。
        '''
        self.symbols[kind][name] = (type, kind, self.index[kind])
        self.index[kind] += 1

    def var_count(self, kind):
        '''
        指定された種類の識別子の数を返す。
        '''
        return sum(1 for n, (t, k, i) in self.symbols[kind].items() if k == kind)
    
    def class_symbols_view(self):
        print(self.class_symbols)
