#!python
import sys,os,html
from collections import deque
from typing import List,Dict

# include
from n2t_jack_analyzer_constant import *

class N2TJackAnalyzer(object):

    def __init__(self, target_file_path: str):
        pass

    def run(self):

        # パラメータからコンパイル対象を取得
        jack_files = self.prepare_file_paths(target_file_path)              # 入力ファイル名と出力ファイル名を設定
        
        # 1ファイルごとにJackコードをコンパイルする
        for jack_file in jack_files:
            ce = CompilationEngine(jack_file)
            ce.compile_jack

    def prepare_file_paths(self, file_path:str) -> List[str]:
        """
        入力Jackファイル名を取得する
        """
        print(" file_path = " + file_path)

        # ファイル指定の場合
        if file_path.endswith('.jack'):

            # 入力ファイル名を self.jack_files に設定
            jack_files = [file_path]

        # ファイル指定意外の場合
        else:
            # --------------------------
            # ディレクトリ指定の場合
            # --------------------------
            # 最後の '/' を削除
            file_path = file_path.rstrip('/')

            # os.walk を使ってディレクトリパス、ディレクトリ名、ファイル名を取得
            dirpath, dirnames, filenames = next(os.walk(file_path), ([], [], []))

            # 末尾に '.jack' を含むファイルのみ対象とする
            jack_files = [filename for filename in filenames if filename.endswith('.jack')]

            # 入力ファイル名を self.jack_files に設定（複数ファイルを想定）
            jack_files = [f"{file_path}/{jack_file}" for jack_file in jack_files]

        for jack_file in jack_files:
            print(" target_jack_file = " + jack_file)

        # 入力ファイルの存在チェック
        try:
            for file_name in jack_files:
                if not os.path.exists(file_name):
                    raise FileNotFoundError(f"ERROR : \"{file_name}\" does not exist.")
                else:
                    return jack_files
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            sys.exit(0)

class CompilationEngine(object):

    def __init__(self,jack_filename):

        # 構文解析XML出力用
        output_xml_filename = jack_filename.replace('.jack', '.xml')
        self.output_xml_file = open(output_xml_filename, 'w')
        self.indent_lv = 0              # インデントレベルを保持する(xml出力用)

        # オブジェクト初期化
        self.jt = JackTokenizer(jack_filename)
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(jack_filename)

        # クラス名を保持する
        self.class_name = None

    #######################
    ## API START ##########
    #ce.write_token(T_KEYWORD, jt.current_token)
    
    @property
    def compile_jack(self):

        if DEBUG_MODE:
            # debug for Tokenizer
            while self.jt.has_more_tokens() :
                self.jt.advance()
        else :
            # 1ファイルごとにJackコードをコンパイルする
            self.jt.advance()
            self.compile_class()
        
        self.jt.output_close()
        self.output_close()
        self.vm_writer.output_close()

        #print("------------------------------------")
        #print(self.symbol_table)
        #print("------------------------------------")

    ## API END ############
    #######################

    #######################
    # プログラム構造
    #######################
    def compile_class(self):
        '''
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.output_nonterminal(KW_CLASS,START_TAG)

        self.output_terminal_and_advance(T_KEYWORD)
        
        self.class_name=self.jt.current_token
        self.output_terminal_and_advance(T_IDENTIFIER)
        
        self.output_terminal_and_advance(T_SYMBOL)
        
        # classVarDec*
        while (self.jt.token_type == T_KEYWORD and self.jt.current_token in (KW_STATIC,KW_FIELD)):
            self.compile_class_var_dec()

        # subroutineDec*
        while (self.jt.token_type == T_KEYWORD and self.jt.current_token in (KW_CONSTRUCTOR,KW_FUNCTION,KW_METHOD)):
            self.compile_subroutine()

        self.output_terminal(T_SYMBOL)
        #self.jt.advance <= classは最終要素のため、advance しない
        
        self.output_nonterminal(KW_CLASS,END_TAG)

    def compile_class_var_dec(self):
        '''
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        '''
        self.output_nonterminal('classVarDec',START_TAG)

        # kind = ('static' | 'field')
        kind=self.jt.current_token
        self.output_terminal_and_advance(T_KEYWORD)
        
        # type = ('int' | 'char' | 'boolean' | className)
        type=self.jt.current_token
        self.output_terminal_and_advance(self.jt.token_type)
        
        # name = identifier
        name=self.jt.current_token
        self.symbol_table.define(name, type, kind)

        self.output_terminal_and_advance(T_IDENTIFIER)

        while self.jt.token_type == T_SYMBOL and self.jt.current_token == ',':
            self.output_terminal_and_advance(T_SYMBOL)
            self.symbol_table.define(self.jt.current_token, type,kind)
            self.output_terminal_and_advance(T_IDENTIFIER)
        self.output_terminal_and_advance(T_SYMBOL)

        self.output_nonterminal('classVarDec',END_TAG)

    def compile_subroutine(self):
        '''
        subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        '''
        self.symbol_table.start_subroutine()    # subroutineBodyの開始時に、subroutineSymbolsを初期化
        self.while_count = -1
        self.if_count = -1

        self.output_nonterminal('subroutineDec',START_TAG)
        
        subroutine_type=self.jt.current_token
        if subroutine_type == KW_METHOD:
            self.symbol_table.define(KW_THIS, self.class_name, SK_ARG)
        self.output_terminal_and_advance(T_KEYWORD)
        if self.jt.token_type == T_KEYWORD and self.jt.current_token == KW_VOID:
            self.output_terminal_and_advance(T_KEYWORD)
        else:
            self.output_terminal_and_advance(self.jt.token_type)
        self.subroutine_name=self.jt.current_token
        self.output_terminal_and_advance(T_IDENTIFIER)
        self.output_terminal_and_advance(T_SYMBOL)
        self.compile_parameter_list()
        self.output_terminal_and_advance(T_SYMBOL)

        # subroutineBody
        self.output_nonterminal('subroutineBody',START_TAG)
        self.output_terminal_and_advance(T_SYMBOL)
        while(self.jt.token_type == T_KEYWORD and self.jt.current_token == KW_VAR):
            self.compile_var_dec()

        self.vm_writer.write_function(f"{self.class_name}.{self.subroutine_name}",self.symbol_table.var_count(SK_VAR))
        if subroutine_type == KW_CONSTRUCTOR:
            self.vm_writer.push_const(self.symbol_table.var_count(SK_FIELD))    # object size
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.pop_this_ptr()
        elif subroutine_type == KW_METHOD:
            self.vm_writer.push_arg(0)
            self.vm_writer.pop_this_ptr()

        self.compile_statements()
        self.output_terminal_and_advance(T_SYMBOL)

        self.output_nonterminal('subroutineBody',END_TAG)

        self.output_nonterminal('subroutineDec',END_TAG)

    def compile_parameter_list(self):
        '''
        parameterList: ((type varName) (',' type varName)*)?
        '''
        self.output_nonterminal('parameterList',START_TAG)
        while self.jt.token_type in (T_KEYWORD,T_IDENTIFIER):
            kind=SK_ARG
            type=self.jt.current_token
            self.output_terminal_and_advance(self.jt.token_type)
            name=self.jt.current_token
            self.output_terminal_and_advance(T_IDENTIFIER)
            self.symbol_table.define(name,type,kind)
            while self.jt.token_type == T_SYMBOL and self.jt.current_token == ',':
                self.output_terminal_and_advance(T_SYMBOL)
                type=self.jt.current_token
                self.output_terminal_and_advance(T_KEYWORD)
                name=self.jt.current_token
                self.output_terminal_and_advance(T_IDENTIFIER)
                self.symbol_table.define(name,type,kind)

        self.output_nonterminal('parameterList',END_TAG)

    def compile_var_dec(self):
        '''
        varDec: 'var' type varName (',' varName)* ';'
        '''
        self.output_nonterminal('varDec',START_TAG)
        kind=SK_VAR
        self.output_terminal_and_advance(T_KEYWORD)
        type=self.jt.current_token
        self.output_terminal_and_advance(self.jt.token_type)
        name=self.jt.current_token
        self.output_terminal_and_advance(T_IDENTIFIER)
        self.symbol_table.define(name, type,kind)
        while self.jt.token_type == T_SYMBOL and self.jt.current_token == ',':
            self.output_terminal_and_advance(T_SYMBOL)
            name=self.jt.current_token
            self.output_terminal_and_advance(T_IDENTIFIER)
            self.symbol_table.define(name, type,kind)
        self.output_terminal_and_advance(T_SYMBOL)

        self.output_nonterminal('varDec',END_TAG)

    #######################
    # 文
    #######################
    def compile_statements(self):
        '''
        statements: statement*
        '''
        self.output_nonterminal('statements',START_TAG)

        while(self.jt.token_type == T_KEYWORD):

            if(self.jt.current_token == KW_LET):
                self.compile_let()

            elif(self.jt.current_token == KW_IF):
                self.compile_if()

            elif(self.jt.current_token == KW_WHILE):
                self.compile_while()

            elif(self.jt.current_token == KW_DO):
                self.compile_do()

            elif(self.jt.current_token == KW_RETURN):
                self.compile_return()
            else:
                raise Exception("compile_statements: unknown token")

        self.output_nonterminal('statements',END_TAG)

    def compile_let(self):
        '''
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        '''
        self.output_nonterminal('letStatement',START_TAG)
        
        self.output_terminal_and_advance(T_KEYWORD)

        # varName データ変換
        symbol_name=self.jt.current_token
        (type, kind, index) = self.symbol_table.get_symbol_info(symbol_name)

        self.output_terminal_and_advance(T_IDENTIFIER)
        # ('[' expression ']')?
        is_array=False
        if(self.jt.token_type == T_SYMBOL and self.jt.current_token == '['):
            is_array=True

            self.output_terminal_and_advance(T_SYMBOL)
            self.compile_expression()
            self.output_terminal_and_advance(T_SYMBOL)

            #VMコード出力
            self.vm_writer.write_push(SEGMENTS_DICT[kind],index)
            self.vm_writer.write_arithmetic(BIN_OP_DICT[OP_ADD])


        self.output_terminal_and_advance(T_SYMBOL) # '='
        self.compile_expression()
        self.output_terminal_and_advance(T_SYMBOL) # ';'

        self.output_nonterminal('letStatement',END_TAG)
        
        if is_array:
            self.vm_writer.pop_temp(0)
            self.vm_writer.pop_that_ptr()
            self.vm_writer.push_temp(0)
            self.vm_writer.pop_that()
        else:
            self.vm_writer.write_pop(SEGMENTS_DICT[kind],index)

    def compile_if(self):
        '''
        ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        '''

        self.output_nonterminal('ifStatement',START_TAG)

        self.output_terminal_and_advance(T_KEYWORD)
        self.output_terminal_and_advance(T_SYMBOL)
        
        self.compile_expression()
        if_label=self.new_if_label()
        self.vm_writer.write_if(f"IF_TRUE{if_label}")
        
        self.output_terminal_and_advance(T_SYMBOL)
        self.output_terminal_and_advance(T_SYMBOL)
        
        self.vm_writer.write_goto(f"IF_FALSE{if_label}")
        self.vm_writer.write_label(f"IF_TRUE{if_label}")

        self.compile_statements()        
        self.output_terminal_and_advance(T_SYMBOL)

        # ('else' '{' statements '}')?
        if(self.jt.token_type == T_KEYWORD and self.jt.current_token == 'else'):
            self.vm_writer.write_goto(f"IF_END{if_label}")
            self.output_terminal_and_advance(T_KEYWORD)
            self.output_terminal_and_advance(T_SYMBOL)
            self.vm_writer.write_label(f"IF_FALSE{if_label}")
            self.compile_statements()
            self.output_terminal_and_advance(T_SYMBOL)
            self.vm_writer.write_label(f"IF_END{if_label}")
        else:
            self.vm_writer.write_label(f"IF_FALSE{if_label}")

        self.output_nonterminal('ifStatement',END_TAG)

    def compile_while(self):
        '''
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        '''
        self.output_nonterminal('whileStatement',START_TAG)

        self.output_terminal_and_advance(T_KEYWORD)

        while_label=self.new_while_label()
        self.vm_writer.write_label(f"WHILE_EXP{while_label}")

        # '(' expression ')'
        self.output_terminal_and_advance(T_SYMBOL)
        self.compile_expression()
        self.vm_writer.write_arithmetic(UNARY_OP_DICT[OP_NOT])
        self.vm_writer.write_if(f"WHILE_END{while_label}")
        self.output_terminal_and_advance(T_SYMBOL)

        # '{' statements '}'
        self.output_terminal_and_advance(T_SYMBOL)
        self.compile_statements()
        self.output_terminal_and_advance(T_SYMBOL)

        self.vm_writer.write_goto(f"WHILE_EXP{while_label}")
        self.vm_writer.write_label(f"WHILE_END{while_label}")

        self.output_nonterminal('whileStatement',END_TAG)
    
    def compile_do(self):
        '''
        doStatement: 'do' subroutineCall ';'
        '''
        self.output_nonterminal('doStatement',START_TAG)
        
        self.output_terminal_and_advance(T_KEYWORD)
        
        self.compile_subroutine_call()
        self.vm_writer.pop_temp(0)

        self.output_terminal_and_advance(T_SYMBOL)

        self.output_nonterminal('doStatement',END_TAG)
    
    def compile_return(self):
        ''''
        returnStatement: 'return' expression? ';'
        '''
        self.output_nonterminal('returnStatement',START_TAG)
        
        self.output_terminal_and_advance(T_KEYWORD)
        
        # expression? (戻り値がある場合は式の評価、無い場合は定値(0)を返却)
        if(self.jt.token_type != T_SYMBOL and self.jt.current_token != ';'):
            self.compile_expression()
        else:
            self.vm_writer.push_const(0)

        self.vm_writer.write_return() 
        self.output_terminal_and_advance(T_SYMBOL)

        self.output_nonterminal('returnStatement',END_TAG)

    #######################
    # 式
    #######################
    def compile_expression_list(self):
        '''
        expressionList: (expression (',' expression)* )?
        '''
        self.output_nonterminal('expressionList',START_TAG)

        arg_count=0

        if self.jt.current_token != ')':
            self.compile_expression()
            arg_count=1
            
            while self.jt.token_type == T_SYMBOL and self.jt.current_token == ',':
                self.output_terminal_and_advance(T_SYMBOL)
                self.compile_expression()
                arg_count+=1

        self.output_nonterminal('expressionList',END_TAG)
        
        return arg_count

    def compile_expression(self):
        '''
        expression: term (op term)*
        '''
        self.output_nonterminal('expression',START_TAG)

        self.compile_term()
        while self.jt.token_type == T_SYMBOL and self.jt.current_token in BIN_OP_DICT:
            op_symbol=self.jt.current_token
            vm_op=BIN_OP_DICT[op_symbol]
            self.output_terminal_and_advance(T_SYMBOL)
            self.compile_term()
            self.vm_writer.write_arithmetic(vm_op)

        self.output_nonterminal('expression',END_TAG)

    def compile_term(self):
        '''
        term: integerConstant | stringConstant | keywordConstant |
              varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        '''
        self.output_nonterminal('term',START_TAG)

        # integerConstant
        if self.jt.token_type == T_INT_CONST :
            self.vm_writer.push_const(self.jt.current_token)
            self.output_terminal_and_advance(T_INT_CONST)
        
        # stringConstant
        elif self.jt.token_type == T_STR_CONST :
            str=self.jt.current_token
            self.vm_writer.push_const(len(str))
            self.vm_writer.write_call('String.new',1)
            for c in str:
                self.vm_writer.push_const(ord(c))
                self.vm_writer.write_call('String.appendChar',2)
            self.output_terminal_and_advance(T_STR_CONST)

        # keywordConstant
        elif self.jt.token_type == T_KEYWORD and self.jt.current_token in (KW_TRUE,KW_FALSE,KW_NULL,KW_THIS):

            keyword=self.jt.current_token
            if keyword == KW_TRUE:
                self.vm_writer.push_const(0)
                self.vm_writer.write_arithmetic(UNARY_OP_DICT[OP_NOT])

            elif keyword in (KW_FALSE,KW_NULL):
                self.vm_writer.push_const(0)

            elif keyword == KW_THIS:
                self.vm_writer.push_this_ptr()

            self.output_terminal_and_advance(T_KEYWORD)

        # '(' expression ')'
        elif self.jt.token_type == T_SYMBOL and self.jt.current_token == '(':
            self.output_terminal_and_advance(T_SYMBOL)
            self.compile_expression()
            self.output_terminal_and_advance(T_SYMBOL)

        # unaryOp term
        elif self.jt.token_type == T_SYMBOL and self.jt.current_token in ('-','~'):
            vm_op=UNARY_OP_DICT[self.jt.current_token]
            self.output_terminal_and_advance(T_SYMBOL)
            self.compile_term()
            self.vm_writer.write_arithmetic(vm_op)

        # subroutineCall
        elif self.jt.peek() in ('(','.'):
            self.compile_subroutine_call()

        # varName '[' expression ']'
        elif self.jt.peek() == ('['):
            ident_name=self.jt.current_token
            (type, kind, index) = self.symbol_table.get_symbol_info(ident_name)

            self.output_terminal_and_advance(T_IDENTIFIER)
            self.output_terminal_and_advance(T_SYMBOL)
            self.compile_expression()
            self.output_terminal_and_advance(T_SYMBOL)

            self.vm_writer.write_push(SEGMENTS_DICT[kind],index)
            self.vm_writer.write_arithmetic(BIN_OP_DICT[OP_ADD])
            self.vm_writer.pop_that_ptr()   # pop  pointer 1
            self.vm_writer.push_that()      # push that 0
            
        # varname
        else:
            ident_name=self.jt.current_token
            (type, kind, index) = self.symbol_table.get_symbol_info(ident_name)
            self.vm_writer.write_push(SEGMENTS_DICT[kind],index)
            self.output_terminal_and_advance(T_IDENTIFIER)

        self.output_nonterminal('term',END_TAG)

    #######################
    # common_parts & utility
    #######################
    def new_if_label(self):
        self.if_count += 1
        return str(self.if_count)
    
    def new_while_label(self):
        self.while_count += 1
        return str(self.while_count)
    
    def compile_subroutine_call(self):
        '''
        subroutineCall: subroutineName '(' expressionList ')' |
                        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        subroutine_type = None
        arg_count = 0

        ident_name=self.jt.current_token
        next_token=self.jt.peek()
        (type, kind, index) = self.symbol_table.get_symbol_info(ident_name)
        if next_token == '(':
            subroutine_type=METHOD_OWN
        elif next_token == '.': 
            if kind is None:
                subroutine_type=FUNCTION
            else:
                subroutine_type=METHOD_OTHER

        # subroutineName | (className | varName)
        self.output_terminal_and_advance(T_IDENTIFIER)

        if subroutine_type == METHOD_OWN:

            # subroutine名は、{自class名}.{method名}
            subroutine_fullname=f"{self.class_name}.{ident_name}"
            
            # thisポインタを渡すためにパラメータ数は +1 する
            self.vm_writer.push_this_ptr()
            arg_count += 1

        elif subroutine_type == METHOD_OTHER:

            # '.' subroutineName
            self.output_terminal_and_advance(T_SYMBOL)
            method_name=self.jt.current_token
            self.output_terminal_and_advance(T_IDENTIFIER)

            # subroutine名は、{methodの所属class名}.{method名}
            subroutine_fullname=f"{type}.{method_name}"

            # thisポインタを渡すためにパラメータ数は +1 する
            self.vm_writer.write_push(SEGMENTS_DICT[kind],index) # field(this) の index番号 をpush
            arg_count += 1

        elif subroutine_type == FUNCTION:

            # '.' subroutineName
            self.output_terminal_and_advance(T_SYMBOL)
            function_name=self.jt.current_token
            self.output_terminal_and_advance(T_IDENTIFIER)

            # subroutine名は、{functionの所属class名}.{function名}
            subroutine_fullname=f"{ident_name}.{function_name}"
        
        else:
            raise Exception(f"invalid subroutine_type={subroutine_type}")
            
        #'(' expressionList ')'
        self.output_terminal_and_advance(T_SYMBOL)
        arg_count+=self.compile_expression_list()
        self.output_terminal_and_advance(T_SYMBOL)

        self.vm_writer.write_call(subroutine_fullname,arg_count)

    def output_terminal_and_advance(self,tag):
        self.output_terminal(tag)
        self.jt.advance()

    def output_nonterminal(self,tag,is_start_tag):
        '''
            tag          : タグ名\n
            is_start_tag : True = 開始タグ , False = 終了タグ\n
                           Trueの場合は、indent_lvをincrement、Falseの場合は decrement
        '''

        # 終了タグの場合はインデントレベルを下げる
        if not is_start_tag:
            self.indent_lv -= 1

        indent_blank = '  ' * self.indent_lv
        # 非ターミナル要素の場合
        if is_start_tag :
            #print(f"{indent_blank}<{tag}>")
            print(f"{indent_blank}<{tag}>",file=self.output_xml_file)
        else :
            #print(f"{indent_blank}</{tag}>")
            print(f"{indent_blank}</{tag}>",file=self.output_xml_file)

        # 開始タグの場合はインデントレベルを上げる
        if is_start_tag:
            self.indent_lv += 1

    def output_terminal(self,tag):
        indent_blank = '  ' * self.indent_lv
        element=html.escape(self.jt.current_token, quote=False)
        print(f"{indent_blank}<{tag}> {element} </{tag}>",file=self.output_xml_file)

    def output_close(self):
        self.output_xml_file.close()

class JackTokenizer(object):
    def __init__(self,jack_filename):

        t_xml_filename = jack_filename.replace('.jack', 'T.xml')
        self.output_xml_file = open(t_xml_filename, 'w')
        self.write_init()

        self.jack_words = self.load_file(jack_filename) 

        self.current_token = None
        self.current_token_type = None
        self.current_token_type_tag = None

    ## API ##
    def has_more_tokens(self):
        return len(self.jack_words) > 0
    
    def peek(self):
        # deque オブジェクトが空でないかをチェック
        if len(self.jack_words) > 0:
            return (self.jack_words[0])[0]  # 先頭文字の1文字目を返す
        else:
            return None  # もしくは適切なデフォルト値
    
    def advance(self):
        if len(self.jack_words) > 0:  # deque オブジェクトが空でないかをチェック
            self.next_token = self.jack_words.popleft()
            self.lex()
        else:
            pass

    def output_line(self):
        self.current_token_type_tag = self.token_type
        try:
            print(f"<{self.current_token_type_tag}> {html.escape(self.current_token, quote=False)} </{self.current_token_type_tag}>",file=self.output_xml_file)
        except ValueError:
            print("Cannot write to a closed file.")

    def output_close(self):
        try:
            print("</tokens>",file=self.output_xml_file)
        except ValueError:
            print("Cannot write to a closed file.")

        self.output_xml_file.close()

    ## Internal ##
    def lex(self):
        next_token=self.next_token

        # Case:symbol
        if next_token[0] in SYMBOLS_LIST:
            self.token_type = T_SYMBOL
            self.current_token = next_token[0]
            if next_token[1:] :
                self.jack_words.appendleft(next_token[1:])
            self.output_line()    # トークナイザ結果出力 (-> xxxT.xml)
            return

        # Case:integerConstant
        if next_token[0].isdigit():
            self.token_type = T_INT_CONST
            current_int = next_token[0:]
            full_int = ''

            for i, num in enumerate(current_int):
                #if not num.isdigit():
                if num in SYMBOLS_LIST:
                    full_int += current_int[:i]
                    if(current_int[i:]):
                        self.jack_words.appendleft(current_int[i:])
                    self.current_token = full_int.strip()
                    self.output_line()    # トークナイザ結果出力 (-> xxxT.xml)
                    return
            self.current_token = current_int.strip()
            self.output_line()    # トークナイザ結果出力 (-> xxxT.xml)
            return

        # Case:stringContant
        if next_token[0] == '"':                                                # トークンの先頭が'"' の場合、"STRING_CONST" の開始と判断する
            self.token_type = T_STR_CONST
            current_string = next_token[1:]                                     # トークンの２文字目から最後まで current_string に代入
            full_string = ''                                                    # 最終的な文字列定数を保持するfull_stringを空文字列で初期化
            while True:                                                         # 文字列定数の終端が見つかるまで無限ループを開始
                for i, char in enumerate(current_string):                       # 現在の文字列の各文字に対して
                    if char == '"':                                             # 文字がダブルクォーテーションなら、文字列定数の終端と判断
                        full_string += current_string[:i]                       # 終了クォートの前の文字を全文字列に追加
                        if current_string[i+1:]:                                # 終了クォートの後に文字がある場合
                            self.jack_words.appendleft(current_string[i+1:])    # それらをjack_wordsの先頭に追加
                        self.current_token = full_string
                        
                        self.output_line()                                        # トークナイザ結果出力 (-> xxxT.xml)
                        return                                                  # 文字列定数が完全に処理されたので、関数を終了
                full_string += current_string + ' '                             # 終了クォートが見つからない場合、現在の文字列とスペースを全文字列に追加
                current_string = self.jack_words.popleft()                      # jack_wordsから次のトークンを取得し、ループを続行

        # Case:keyword or identifier
        self.current_token = next_token
        for i, word in enumerate(next_token):
            # 末尾のシンボルのチェック
            if word in SYMBOLS_LIST:
                # シンボルだった場合、
                # シンボルの前までをキーワードとして切り出し、末尾シンボルをjack_wordsの先頭に追加する(次回判定用)
                self.current_token = next_token[:i]
                self.jack_words.appendleft(next_token[i:])
                break
        
        # キーワードの判定
        if self.current_token in KEYWORDS_LIST:
            self.token_type = T_KEYWORD
        else:
            self.token_type = T_IDENTIFIER
        
        self.output_line()                                                        # トークナイザ結果出力 (-> xxxT.xml)
        return
    


    def write_init(self):
        print("<tokens>",file=self.output_xml_file)

    def load_file(self, jack_filename: str) -> deque:
        
        #print(f' - Loading {jack_filename}')
        with open(jack_filename, 'r',encoding='utf-8') as f:
            contents = f.read()

        # 改行コードで分割する
        contents = contents.split('\n')

        # コメントを除去する
        contents = [l.split('//')[0] for l in contents]

        # 先頭と末尾の空白文字を削除する
        contents = [l.strip() for l in contents]
        
        # ブロックコメントを除去する
        in_comment = False
        for i, line in enumerate(contents):
            start, end = line[:2], line[-2:]
            if start == '/*':
                in_comment = True

            if in_comment:
                contents[i] = ''

            if start == '*/' or end == '*/':
                in_comment = False
        
        # 空白行を除去する
        contents = [l for l in contents if l != '']
        
        # contentsを空白で分割しワード単位のリストにする
        words = []
        for line in contents:
            words.extend(line.split())

        # リストをデックに変換して返す
        return deque(words)

class SymbolTable(object):
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.symbols_tbl = {SK_STATIC: self.class_symbols
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
            result += 'symbol name:'+str(n)+', type:'+str(t)+', kind:'+str(k)+', index:'+str(i)+'\n'
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
        self.symbols_tbl[kind][name] = (type, kind, self.index[kind])
        self.index[kind] += 1

    def var_count(self, kind):
        '''
        指定された種類の識別子の数を返す。
        '''
        count = sum(1 for _, (_, k, _) in self.symbols_tbl[kind].items() if k == kind)
        return count

    def type_of(self, name):
        '''
        指定された名前の識別子の型を返す。
        '''
        (type,_,_) = self.get_symbol_info(name)
        return type
        
    def kind_of(self, name):
        '''
        指定された名前の識別子の種類を返す。
        STATIC,FIELD,ARG,VAR, NONE のいずれか。
        '''
        (_,kind,_) = self.get_symbol_info(name)
        return kind

    def index_of(self, name):
        '''
        指定された名前の識別子のインデックスを返す。
        '''
        (_,_,index) = self.get_symbol_info(name)
        return index

    def get_symbol_info(self, name):
        '''
        指定された名前の識別子の情報を返す。
        '''
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name]
        elif name in self.class_symbols:
            return self.class_symbols[name]
        else:
            return (None, None, None)
        
    def class_symbols_view(self):
        print(self.class_symbols)

class VMWriter(object):
    '''
    パース内容に応じてVMコマンドを書き込む
    '''
    def __init__(self, jack_filename):
        self.vm_filename = jack_filename.replace('.jack', '.vm')
        self.output_vm_file = open(self.vm_filename, 'w')

    # Extend API
    def push_const(self, val):
        self.write_push('constant', val)
        
    def push_arg(self, arg_num):
        self.write_push('argument', arg_num)
        
    def push_this_ptr(self):
        self.write_push('pointer', 0)
        
    def pop_this_ptr(self):
        self.write_pop('pointer', 0)
        
    def pop_that_ptr(self):
        self.write_pop('pointer', 1)
        
    def push_that(self):
        self.write_push('that', 0)
        
    def pop_that(self):
        self.write_pop('that', 0)
        
    def push_temp(self, temp_num):
        self.write_push('temp', temp_num)
        
    def pop_temp(self, temp_num):
        self.write_pop('temp', temp_num)

    # Basic API
    def write_push(self, segment, index):
        self.write_vm('push', segment, index)

    def write_pop(self, segment, index):
        self.write_vm('pop', segment, index)

    def write_arithmetic(self, command):
        self.write_vm(command)
    
    def write_label(self, label):
        self.write_vm(f"label {label}")
    
    def write_goto(self, label):
        self.write_vm(f"goto {label}")

    def write_if(self, label):
        self.write_vm(f"if-goto {label}")
    
    def write_call(self, name, n_args):
        self.write_vm('call', name, n_args)

    def write_function(self, name, n_locals):
        self.write_vm('function', name, n_locals)

    def write_return(self):
        self.write_vm(KW_RETURN)
    
    def output_close(self):
        self.output_vm_file.close()

    # Internal method
    def write_vm(self, vm_command, arg1="", arg2=""):
        print(f"{vm_command} {arg1} {arg2}", file=self.output_vm_file)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 n2t_jack_analyzer.py <input_file> or <input_dir>")
        sys.exit(1)

    print("Jack Analyze Start")
    target_file_path  = sys.argv[1]

    vm_translator = N2TJackAnalyzer(target_file_path)
    vm_translator.run()

    print("Jack Analyze End")

