#!python
import sys,os,html
from collections import deque
from typing import List,Dict

#######################
# 定数
#######################
ANALYZE_MODE = 'xml' # 'xml' or 'vm'

JACK_COMENT_1 = '//'
VM_TRUE   = '-1'
VM_FALSE  = '0'

TERMINAL=True
NON_TERMINAL=False
START_TAG=True
END_TAG=False

TOKEN_TAG_DICT = {
    'KEYWORD'     : 'keyword',
    'SYMBOL'      : 'symbol',
    'IDENTIFIER'  : 'identifier',
    'INT_CONST'   : 'integerConstant',
    'STRING_CONST': 'stringConstant',
}

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

        # debug for Tokenizer
        #while self.jt.has_more_tokens :
        #    self.jt.advance
        #self.jt.output_close

        # 1ファイルごとにJackコードをコンパイルする
        self.jt.advance
        self.compile_class()
        self.jt.output_close
        self.output_close()

    ## API END ############
    #######################

    #######################
    # プログラム構造
    #######################
    def compile_class(self):
        '''
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.output_nonterminal('class',START_TAG)

        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance('identifier')
        self.output_terminal_and_advance('symbol')
        
        # classVarDec*
        while (self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('static','field')):
            self.compile_class_var_dec()
        
        # subroutineDec*
        while (self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('constructor','function','method')):
            self.compile_subroutine()

        self.output_terminal('symbol')
        #self.jt.advance <= classは最終要素のため、advance しない
        
        self.output_nonterminal('class',END_TAG)

    def compile_class_var_dec(self):
        '''
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        '''
        self.output_nonterminal('classVarDec',START_TAG)

        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance(TOKEN_TAG_DICT[self.jt.token_type])
        self.output_terminal_and_advance('identifier')
        while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
            self.output_terminal_and_advance('symbol')
            self.output_terminal_and_advance('identifier')
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('classVarDec',END_TAG)

    def compile_subroutine(self):
        '''
        subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        '''
        self.output_nonterminal('subroutineDec',START_TAG)

        self.output_terminal_and_advance('keyword')
        if self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'void':
            self.output_terminal_and_advance('keyword')
        else:
            self.output_terminal_and_advance(TOKEN_TAG_DICT[self.jt.token_type])
        self.output_terminal_and_advance('identifier')
        self.output_terminal_and_advance('symbol')
        self.compile_parameter_list()
        self.output_terminal_and_advance('symbol')

        # subroutineBody
        self.output_nonterminal('subroutineBody',START_TAG)

        self.output_terminal_and_advance('symbol')
        while(self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'var'):
            self.compile_var_dec()
        self.compile_statements()
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('subroutineBody',END_TAG)

        self.output_nonterminal('subroutineDec',END_TAG)

    def compile_parameter_list(self):
        '''
        parameterList: ((type varName) (',' type varName)*)?
        '''
        self.output_nonterminal('parameterList',START_TAG)

        while self.jt.token_type in ('KEYWORD','IDENTIFIER'):
            self.output_terminal_and_advance(TOKEN_TAG_DICT[self.jt.token_type])
            self.output_terminal_and_advance('identifier')
            while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
                self.output_terminal_and_advance('symbol')
                self.output_terminal_and_advance('keyword')
                self.output_terminal_and_advance('identifier')

        self.output_nonterminal('parameterList',END_TAG)

    def compile_var_dec(self):
        '''
        varDec: 'var' type varName (',' varName)* ';'
        '''
        self.output_nonterminal('varDec',START_TAG)

        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance(TOKEN_TAG_DICT[self.jt.token_type])
        self.output_terminal_and_advance('identifier')
        while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
            self.output_terminal_and_advance('symbol')
            self.output_terminal_and_advance('identifier')
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('varDec',END_TAG)

    #######################
    # 文
    #######################
    def compile_statements(self):
        '''
        statements: statement*
        '''
        self.output_nonterminal('statements',START_TAG)

        while(self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('do','let','while','return','if')):

            if(self.jt.current_token == 'let'):
                self.compile_let()

            elif(self.jt.current_token == 'if'):
                self.compile_if()

            elif(self.jt.current_token == 'while'):
                self.compile_while()

            elif(self.jt.current_token == 'do'):
                self.compile_do()

            elif(self.jt.current_token == 'return'):
                self.compile_return()

        self.output_nonterminal('statements',END_TAG)

    def compile_let(self):
        '''
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        '''
        self.output_nonterminal('letStatement',START_TAG)
        
        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance('identifier')
        # ('[' expression ']')?
        if(self.jt.token_type == 'SYMBOL' and self.jt.current_token == '['):
            self.output_terminal_and_advance('symbol')
            self.compile_expression()
            self.output_terminal_and_advance('symbol')
        self.output_terminal_and_advance('symbol')
        self.compile_expression()
        self.output_terminal_and_advance('symbol')
        
        self.output_nonterminal('letStatement',END_TAG)

    def compile_if(self):
        '''
        ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        '''
        self.output_nonterminal('ifStatement',START_TAG)
        
        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance('symbol')
        self.compile_expression()
        self.output_terminal_and_advance('symbol')
        self.output_terminal_and_advance('symbol')
        self.compile_statements()
        self.output_terminal_and_advance('symbol')
        if(self.jt.token_type == 'KEYWORD' and self.jt.current_token == 'else'):
            self.output_terminal_and_advance('keyword')
            self.output_terminal_and_advance('symbol')
            self.compile_statements()
            self.output_terminal_and_advance('symbol')

        self.output_nonterminal('ifStatement',END_TAG)

    def compile_while(self):
        '''
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        '''
        self.output_nonterminal('whileStatement',START_TAG)
        
        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance('symbol')
        self.compile_expression()
        self.output_terminal_and_advance('symbol')
        self.output_terminal_and_advance('symbol')
        self.compile_statements()
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('whileStatement',END_TAG)

    def compile_do(self):
        '''
        doStatement: 'do' subroutineCall ';'
        '''
        self.output_nonterminal('doStatement',START_TAG)
        
        self.output_terminal_and_advance('keyword')
        self.output_terminal_and_advance('identifier')
        if self.jt.current_token == '(':
            self.output_terminal_and_advance('symbol')
            self.compile_expression_list()
            self.output_terminal_and_advance('symbol')
        else:
            self.output_terminal_and_advance('symbol')
            self.output_terminal_and_advance('identifier')
            self.output_terminal_and_advance('symbol')
            self.compile_expression_list()
            self.output_terminal_and_advance('symbol')
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('doStatement',END_TAG)

    def compile_return(self):
        ''''
        returnStatement: 'return' expression? ';'
        '''
        self.output_nonterminal('returnStatement',START_TAG)
        
        self.output_terminal_and_advance('keyword')
        if(self.jt.token_type != 'SYMBOL' and self.jt.current_token != ';'):    # ";" 以外の場合は式
            self.compile_expression()
        self.output_terminal_and_advance('symbol')

        self.output_nonterminal('returnStatement',END_TAG)

    #######################
    # 式
    #######################
    def compile_expression(self):
        '''
        expression: term (op term)*
        '''
        self.output_nonterminal('expression',START_TAG)

        self.compile_term()
        while self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('+','-','*','/','&','|','<','>','='):
            self.output_terminal_and_advance('symbol')
            self.compile_term()

        self.output_nonterminal('expression',END_TAG)

    def compile_expression_list(self):
        '''
        expressionList: (expression (',' expression)* )?
        '''
        self.output_nonterminal('expressionList',START_TAG)
        
        if self.jt.current_token != ')':
            self.compile_expression()
            while self.jt.token_type == 'SYMBOL' and self.jt.current_token in (','):
                self.output_terminal_and_advance('symbol')
                self.compile_expression()

        self.output_nonterminal('expressionList',END_TAG)

    def compile_term(self):
        '''
        term: integerConstant | stringConstant | keywordConstant |
              varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        '''
        self.output_nonterminal('term',START_TAG)

        if self.jt.token_type == 'INT_CONST':
            self.output_terminal_and_advance('integerConstant')
        elif self.jt.token_type == 'STRING_CONST':
            self.output_terminal_and_advance('stringConstant')
        elif self.jt.token_type == 'KEYWORD' and self.jt.current_token in ('true','false','null','this'):
            self.output_terminal_and_advance('keyword')
        elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('('):
            self.output_terminal_and_advance('symbol')
            self.compile_expression()
            self.output_terminal_and_advance('symbol')
        elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('-','~'):
            self.output_terminal_and_advance('symbol')
            self.compile_term()
        elif self.jt.token_type == 'IDENTIFIER':
            self.output_terminal_and_advance('identifier')
            if self.jt.token_type == 'SYMBOL' and self.jt.current_token == ('['):
                self.output_terminal_and_advance('symbol')
                self.compile_expression()
                self.output_terminal_and_advance('symbol')
            elif self.jt.token_type == 'SYMBOL' and self.jt.current_token in ('(','.'):
                if self.jt.current_token == '.':
                    self.output_terminal_and_advance('symbol')
                    self.output_terminal_and_advance('identifier')
                self.output_terminal_and_advance('symbol')
                self.compile_expression_list()
                self.output_terminal_and_advance('symbol')
        else:
            self.output_terminal_and_advance('identifier')

        self.output_nonterminal('term',END_TAG)

    #######################
    # utility
    #######################
    def output_terminal_and_advance(self,tag):
        self.output_terminal(tag)
        self.jt.advance

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
            print(f"{indent_blank}<{tag}>",file=self.output_file)
        else :
            #print(f"{indent_blank}</{tag}>")
            print(f"{indent_blank}</{tag}>",file=self.output_file)

        # 開始タグの場合はインデントレベルを上げる
        if is_start_tag:
            self.indent_lv += 1

    def output_terminal(self,tag):
        indent_blank = '  ' * self.indent_lv
        element=html.escape(self.jt.current_token, quote=False)
        print(f"{indent_blank}<{tag}> {element} </{tag}>",file=self.output_file)

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
            #self.current_token = next_token[0:]
            #self.output_line    # トークナイザ結果出力 (-> xxxT.xml)
            #return
            for i, num in enumerate(current_int):
                #if not num.isdigit():
                if num in self.symbols:
                    full_int += current_int[:i]
                    if(current_int[i:]):
                        self.jack_words.appendleft(current_int[i:])
                    self.current_token = full_int.strip()
                    self.output_line    # トークナイザ結果出力 (-> xxxT.xml)
                    return
            self.current_token = current_int.strip()
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
        try:
            print(f"<{self.current_token_type_tag}> {html.escape(self.current_token, quote=False)} </{self.current_token_type_tag}>",file=self.output_file)
        except ValueError:
            print("Cannot write to a closed file.")
        #print(f"<{self.current_token_type_tag}> {html.escape(self.current_token, quote=False)} </{self.current_token_type_tag}>",file=self.output_file)

    @property
    def output_close(self):
        try:
            print("</tokens>",file=self.output_file)
        except ValueError:
            print("Cannot write to a closed file.")
        #print("</tokens>",file=self.output_file)
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

