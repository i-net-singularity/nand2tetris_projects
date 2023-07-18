#!python
import sys,os,html
from collections import deque
from typing import List,Dict

ANALYZE_MODE = 'xml' # 'xml' or 'vm'

JACK_COMENT_1 = '//'
VM_TRUE   = '-1'
VM_FALSE  = '0'

TERMINAL=True
NON_TERMINAL=False
START_TAG=True
END_TAG=False

class N2TJackAnalyzer(object):

    def __init__(self, target_file_path: str):
        
        self.jack_files = []              # jackファイル名を格納するリスト
        self.jack_codes = {}              # ファイルごとに1行ごとのVMコードを格納する
        self.parsed_jack_codes = {}       # ファイルごとにVMコードのパース結果を格納する
        self.vm_codes = []

    def run(self):

        # パラメータからコンパイル対象を取得
        self.jack_files = self.prepare_file_paths(target_file_path)              # 入力ファイル名と出力ファイル名を設定
        
        # 1ファイルごとにJackコードをコンパイルする
        for jack_file in self.jack_files:
            ce = CompilationEngine(jack_file)
            ce.compile_jack

    def prepare_file_paths(self, file_path):
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
        self.jack_filename = jack_filename
        self.jt = JackTokenizer(self.jack_filename)

        self.output_filename = self.jack_filename.replace('.jack', '.xml')
        self.output_file = open(self.output_filename, 'w')

        self.indent_lv = 0


    #######################
    ## API START ##########
    #ce.write_token('keyword', jt.current_token)
    
    @property
    def compile_jack(self):
        
        # 1ファイルごとにJackコードをコンパイルする
        while self.jt.has_more_tokens:
            self.jt.advance
            self.complie_class()

        self.jt.output_close
        self.output_close()


    ## API END ############
    #######################

    def complie_class(self):
        '''
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.output_line_xml('class','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        if(self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'class'):
            
            self.output_terminal('keyword')
            self.jt.advance 
           
            self.output_terminal('identifier')
            self.jt.advance 

            self.output_terminal('symbol')
            self.jt.advance 
            
            # classVarDec*
            while (self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('static','field')):
                self.complie_class_var_dec()
            
            # subroutineDec*
            while (self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('constructor','function','method')):
                self.complie_subroutine()

            self.output_terminal('symbol')
            #self.jt.advance <= 次の要素はないので、advance しない

            self.indent_lv -= 1
            self.output_line_xml('class','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

        else:
            print(f"ERROR : \"{self.jt.current_token}\" is not keyword.", file=self.output_file)
            #exit(0)

    def complie_class_var_dec(self):
        '''
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        '''

        self.output_line_xml('classVarDec','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        while self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('static', 'field'):

            self.output_terminal('keyword')
            
            self.jt.advance

            if self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('int', 'char', 'boolean'):
                self.output_terminal('keyword')
            elif self.jt.token_type == 'IDENTIFIER':
                self.output_terminal('identifier')

            else:
                print(f"ERROR : \"{self.jt.current_token}\" is not keyword.", file=self.output_file)
                #exit(0)
            
            self.jt.advance
            self.output_terminal('identifier')
            
            self.jt.advance

            while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
                self.output_terminal('symbol')
                self.jt.advance
                self.output_terminal('identifier')
                self.jt.advance
            
            self.output_terminal('symbol')

        self.indent_lv -= 1
        self.output_line_xml('classVarDec','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)
            
        self.jt.advance

    def complie_subroutine(self):

        self.output_line_xml('subroutineDec','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        
        self.indent_lv += 1

        self.output_terminal('keyword')
        self.jt.advance

        # ('void' | type)
        if self.jt.token_type == 'KEYWORD':
            self.output_terminal('keyword')
        elif self.jt.token_type == 'IDENTIFIER':
            self.output_terminal('identifier')
        else:
            print(f"ERROR : \"{self.jt.current_token}\" is not keyword.", file=self.output_file)
            #exit(0)
        
        # subroutineName
        self.jt.advance
        self.output_terminal('identifier')

        # '('
        self.jt.advance
        self.output_terminal('symbol')

        # parameterList
        self.jt.advance
        self.complie_parameter_list()
        self.output_terminal('symbol')

        # subroutineBody
        self.jt.advance
        self.complie_subroutine_body()

        self.indent_lv -= 1
        self.output_line_xml('subroutineDec','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_parameter_list(self):
        self.output_line_xml('parameterList','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        while self.jt.token_type in ('KEYWORD','IDENTIFIER'):
            if (self.jt.token_type == 'KEYWORD'):
                self.output_terminal('keyword')
            else :
                self.output_terminal('identifier')

            self.jt.advance
            self.output_terminal('identifier')

            self.jt.advance
            while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
                self.output_terminal('symbol')
                self.jt.advance
                self.output_terminal('keyword')
                self.jt.advance
                self.output_terminal('identifier')
                self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('parameterList','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)
        
    def complie_subroutine_body(self):
        '''
        subroutineBody: '{' varDec* statements '}'
        '''
        self.output_line_xml('subroutineBody','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        #'{'
        self.output_terminal('symbol')
        self.jt.advance
        
        # varDec*
        while(self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'var'):
            self.complie_var_dec()

        # statements
        self.complie_statements()

        #'}'
        self.output_terminal('symbol')
        self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('subroutineBody','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_var_dec(self):
        '''
        varDec: 'var' type varName (',' varName)* ';'
        '''
        self.output_line_xml('varDec','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        # 'var'
        self.output_terminal('keyword')
        self.jt.advance

        # type
        if self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('void', 'int', 'char', 'boolean',):
            self.output_terminal('keyword')
        elif self.jt.token_type == 'IDENTIFIER':
            self.output_terminal('identifier')
        self.jt.advance

        # varName
        self.output_terminal('identifier')
        self.jt.advance

        while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
            self.output_terminal('symbol')
            self.jt.advance

            self.output_terminal('identifier')
            self.jt.advance

        self.output_terminal('symbol')
        self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('varDec','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_statements(self):

        self.output_line_xml('statements','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        while(self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('do','let','while','return','if')):

            if(self.jt.current_token == 'let'):
                self.complie_let()

            elif(self.jt.current_token == 'if'):
                self.complie_if()

            elif(self.jt.current_token == 'while'):
                self.complie_while()

            elif(self.jt.current_token == 'do'):
                self.complie_do()

            elif(self.jt.current_token == 'return'):
                self.complie_return()

        self.indent_lv -= 1
        self.output_line_xml('statements','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_let(self):
        '''
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        '''
        self.output_line_xml('letStatement','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        # 'let'
        self.output_terminal('keyword')
        self.jt.advance
        # varName
        self.output_terminal('identifier')
        self.jt.advance
        # ('[' expression ']')?
        if(self.jt.token_type == 'SYMBOL' and self.jt.current_token == '['):
            # '['
            self.output_terminal('symbol')
            self.jt.advance
            # expression
            self.complie_expression()
            # ']'
            self.output_terminal('symbol')
            self.jt.advance
        
        # '='
        self.output_terminal('symbol')
        self.jt.advance
        # expression
        self.complie_expression()
        # ';'
        self.output_terminal('symbol')
        self.jt.advance
        
        self.indent_lv -= 1
        self.output_line_xml('letStatement','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_if(self):
        '''
        ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        '''
        self.output_line_xml('ifStatement','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        # 'if'
        self.output_terminal('keyword')
        self.jt.advance

        # '('
        self.output_terminal('symbol')
        self.jt.advance

        # expression
        self.complie_expression()

        # ')'
        self.output_terminal('symbol')
        self.jt.advance
        
        # '{'
        self.output_terminal('symbol')
        self.jt.advance

        # statements
        self.complie_statements()

        # '}'
        self.output_terminal('symbol')
        self.jt.advance

        # ('else' '{' statements '}')?
        if(self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'else'):
            self.output_terminal('keyword')
            self.jt.advance

            self.output_terminal('symbol')
            self.jt.advance

            self.complie_statements()

            self.output_terminal('symbol')
            self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('ifStatement','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_while(self):
        '''
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        '''
        self.output_line_xml('whileStatement','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        self.output_terminal('keyword')
        self.jt.advance

        self.output_terminal('symbol')
        self.jt.advance

        self.complie_expression()
        
        self.output_terminal('symbol')
        self.jt.advance

        self.output_terminal('symbol')
        self.jt.advance

        self.complie_statements()

        self.output_terminal('symbol')
        self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('whileStatement','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_do(self):
        self.output_line_xml('doStatement','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        self.output_terminal('keyword')
        self.jt.advance
        
        self.complie_subroutine_call()
        self.jt.advance
        
        self.output_terminal('symbol')
        self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('doStatement','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_return(self):
        self.output_line_xml('returnStatement','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        self.output_terminal('keyword')
        self.jt.advance
        
        # expression? (";"以外の場合は式)
        if(self.jt.token_type != 'SYMBOL' and self.jt.current_token != ';'):
            self.complie_expression()

        self.output_terminal('symbol')
        self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('returnStatement','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_expression(self):
        '''
        expression: term (op term)*
        '''
        self.output_line_xml('expression','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        self.complie_term()
        while self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('+','-','*','/','&','|','<','>','='):
            self.output_terminal('symbol')
            self.jt.advance
            self.complie_term()

        self.indent_lv -= 1
        self.output_line_xml('expression','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_subroutine_call(self):
        self.output_terminal('identifier')
        self.jt.advance
        self.output_terminal('symbol')
        if self.jt.current_token == '(':
            self.jt.advance
            self.complie_expression_list()
            self.output_terminal('symbol')
        else:
            self.jt.advance
            self.output_terminal('identifier')
            self.jt.advance
            self.output_terminal('symbol')
            self.jt.advance
            self.complie_expression_list()
            self.output_terminal('symbol')

    def complie_expression_list(self):
        '''
        expressionList: (expression (',' expression)* )?
        '''
        self.output_line_xml('expressionList','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1
        
        if self.jt.current_token != ')':
            self.complie_expression()
            while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
                self.output_terminal('symbol')
                self.jt.advance
                self.complie_expression()

        self.indent_lv -= 1
        self.output_line_xml('expressionList','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def complie_term(self):
        self.output_line_xml('term','DUMMY',self.indent_lv,NON_TERMINAL,START_TAG)
        self.indent_lv += 1

        if self.jt.token_type == 'INT_CONST':
            self.output_terminal('integerConstant')
            self.jt.advance

        elif self.jt.token_type == 'STRING_CONST':
            self.output_terminal('stringConstant')
            self.jt.advance

        elif self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('true','false','null','this'):
            self.output_terminal('keyword')
            self.jt.advance

        elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('('):
            self.output_terminal('symbol')
            self.jt.advance
            self.complie_expression()
            self.output_terminal('symbol')
            self.jt.advance
        elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('-','~'):
            self.output_terminal('symbol')
            self.jt.advance
            self.complie_term()
        elif self.jt.token_type == 'IDENTIFIER':
            self.output_terminal('identifier')
            self.jt.advance
            if self.jt.token_type == 'SYMBOL' and self.jt.current_token == ('['):
                self.output_terminal('symbol')
                self.jt.advance
                self.complie_expression()
                self.output_terminal('symbol')
                self.jt.advance
            elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('(','.'):

                if self.jt.current_token == '.':
                    self.output_terminal('symbol')
                    self.jt.advance
                    self.output_terminal('identifier')
                    self.jt.advance

                self.output_terminal('symbol')
                self.jt.advance
                self.complie_expression_list()
                self.output_terminal('symbol')
                self.jt.advance

        else:
            self.output_terminal('identifier')
            self.jt.advance

        self.indent_lv -= 1
        self.output_line_xml('term','DUMMY',self.indent_lv,NON_TERMINAL,END_TAG)

    def output_terminal(self,tag):
        self.output_line_xml(tag,self.jt.current_token,self.indent_lv,TERMINAL)

    def output_line_xml(self,tag,element,indent_lv,term_flg,is_start_tag=True):
        '''
            tag        : タグ名\n
            element    : タグ要素\n
            indent_lv  : インデントレベル\n
            term_flg   : True = 終端記号 , Flase = 非終端記号\n
            is_end_tag : 非終端記号の場合のみ有効、True = 開始タグ , False = 終了タグ\n
        '''
        indent_blank = '  ' * indent_lv
        element=html.escape(element, quote=False)
        if term_flg == True:
            # ターミナル要素の場合
            print(f"{indent_blank}<{tag}> {element} </{tag}>")
            print(f"{indent_blank}<{tag}> {element} </{tag}>",file=self.output_file)
        else :
            # 非ターミナル要素の場合
            if is_start_tag :
                print(f"{indent_blank}<{tag}>")
                print(f"{indent_blank}<{tag}>",file=self.output_file)
            else :
                print(f"{indent_blank}</{tag}>")
                print(f"{indent_blank}</{tag}>",file=self.output_file)

    def output_close(self):
        self.output_file.close()

class JackTokenizer(object):
    def __init__(self,jack_filename):
        self.jack_filename = jack_filename
        self.t_xml_filename = self.jack_filename.replace('.jack', 'T.xml')
        self.output_file = open(self.t_xml_filename, 'w')
        self.write_init()

        self.jack_words = self.load_file(self.jack_filename) 

        self.keywords_dict = {
            'class'       : 'CLASS',
            'method'      : 'METHOD',
            'function'    : 'FUNCTION',
            'constructor' : 'CONSTRUCTOR',
            'int'         : 'INT',
            'boolean'     : 'BOOLEAN',
            'char'        : 'CHAR',
            'void'        : 'VOID',
            'var'         : 'VAR',
            'static'      : 'STATIC',
            'field'       : 'FIELD',
            'let'         : 'LET',
            'do'          : 'DO',
            'if'          : 'IF',
            'else'        : 'ELSE',
            'while'       : 'WHILE',
            'return'      : 'RETURN',
            'true'        : 'TRUE',
            'false'       : 'FALSE',
            'null'        : 'NULL',
            'this'        : 'THIS',
        }
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
        self.token_tag_dict = {
            'KEYWORD'     : 'keyword',
            'SYMBOL'      : 'symbol',
            'IDENTIFIER'  : 'identifier',
            'INT_CONST'   : 'integerConstant',
            'STRING_CONST': 'stringConstant',
        }

        self.current_token = None
        self.current_token_type = None
        self.current_token_type_tag = None

    #######################
    ## API START ##########

    @property
    def has_more_tokens(self):
        return len(self.jack_words) > 0
    
    @property
    def advance(self):
        next_token=self.jack_words.popleft()

        # Case:symbol
        if next_token[0] in self.symbols:
            self.token_type = 'SYMBOL'
            self.current_token = next_token[0]
            if next_token[1:] :
                self.jack_words.appendleft(next_token[1:])
            
            self.output_line    # トークナイザ結果出力 (-> xxxT.xml)
            return

        # Case:integerConstant
        if next_token[0].isdigit():
            self.token_type = 'INT_CONST'
            current_int = next_token[0:]
            full_int = ''

            for i, num in enumerate(current_int):
                if not num.isdigit():
                    full_int += current_int[:i]
                    if(current_int[i:]):
                        self.jack_words.appendleft(current_int[i:])
                    self.current_token = full_int.strip()
                    
                    self.output_line    # トークナイザ結果出力 (-> xxxT.xml)
                    return

        # Case:stringContant
        if next_token[0] == '"':                                                # トークンの先頭が'"' の場合、"STRING_CONST" の開始と判断する
            self.token_type = 'STRING_CONST'
            current_string = next_token[1:]                                     # トークンの２文字目から最後まで current_string に代入
            full_string = ''                                                    # 最終的な文字列定数を保持するfull_stringを空文字列で初期化
            while True:                                                         # 文字列定数の終端が見つかるまで無限ループを開始
                for i, char in enumerate(current_string):                       # 現在の文字列の各文字に対して
                    if char == '"':                                             # 文字がダブルクォーテーションなら、文字列定数の終端と判断
                        full_string += current_string[:i]                       # 終了クォートの前の文字を全文字列に追加
                        if current_string[i+1:]:                                # 終了クォートの後に文字がある場合
                            self.jack_words.appendleft(current_string[i+1:])    # それらをjack_wordsの先頭に追加
                        #self.current_token = full_string.strip()                # 現在のトークンを、前後の空白を削除した全文字列として設定
                        self.current_token = full_string
                        
                        self.output_line                                        # トークナイザ結果出力 (-> xxxT.xml)
                        return                                                  # 文字列定数が完全に処理されたので、関数を終了
                full_string += current_string + ' '                             # 終了クォートが見つからない場合、現在の文字列とスペースを全文字列に追加
                current_string = self.jack_words.popleft()                      # jack_wordsから次のトークンを取得し、ループを続行

        # Case:keyword or identifier
        self.current_token = next_token
        for i, word in enumerate(next_token):
            # 末尾のシンボルのチェック
            if word in self.symbols:
                # シンボルだった場合、
                # シンボルの前までをキーワードとして切り出し、末尾シンボルをjack_wordsの先頭に追加する(次回判定用)
                self.current_token = next_token[:i]
                self.jack_words.appendleft(next_token[i:])
                break
        
        # キーワードの判定
        if self.current_token in self.keywords_dict:
            self.token_type = 'KEYWORD'
        else:
            self.token_type = 'IDENTIFIER'
        
        self.output_line                                                        # トークナイザ結果出力 (-> xxxT.xml)
        return

    @property
    def get_token_type(self):
        return self.token_type
    
    @property
    def get_key_word(self):
        return self.keywords_dict[self.current_token]
    
    @property
    def get_symbol(self):
        return self.current_token
    
    @property
    def get_int_val(self):
        return int(self.current_token)

    @property
    def get_identifier(self):
        return self.current_token
    
    @property
    def get_string_val(self):
        return self.current_token
    
    @property
    def output_line(self):
        self.current_token_type_tag = self.token_tag_dict[self.token_type]
        #escaped_s = html.escape(s, quote=False)
        print(f"<{self.current_token_type_tag}> {html.escape(self.current_token, quote=False)} </{self.current_token_type_tag}>",file=self.output_file)

    @property
    def output_close(self):
        print("</tokens>",file=self.output_file)
        self.output_file.close()

    ## API END ############
    #######################

    def write_init(self):
        print("<tokens>",file=self.output_file)

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
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 n2t_jack_analyzer.py <input_file> or <input_dir>")
        sys.exit(1)

    print("Jack Analyze Start")
    target_file_path  = sys.argv[1]

    vm_translator = N2TJackAnalyzer(target_file_path)
    vm_translator.run()

    print("Jack Analyze End")

