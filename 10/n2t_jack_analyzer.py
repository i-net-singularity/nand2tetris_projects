#!python
import sys,os,html
from collections import deque
from typing import List,Dict

ANALYZE_MODE = 'xml' # 'xml' or 'vm'

JACK_COMENT_1 = '//'
VM_TRUE   = '-1'
VM_FALSE  = '0'

class N2TJackAnalyzer(object):

    def __init__(self, target_file_path: str):
        
        self.jack_files = []                # jackファイル名を格納するリスト
        #self.out_file = None

        self.jack_codes = {}              # ファイルごとに1行ごとのVMコードを格納する
        self.parsed_jack_codes = {}       # ファイルごとにVMコードのパース結果を格納する
        self.vm_codes = []

    def run(self):
        self.jack_files = self.prepare_file_paths(target_file_path)              # 入力ファイル名と出力ファイル名を設定
        
        # 1ファイルごとにJackコードをコンパイルする
        for jack_file in self.jack_files:
            out_file_tokenizer = jack_file.replace('.jack', 'T.xml')
            tokenizer = JackTokenizer(jack_file)

            #ce = CompilationEngine(jack_file)
            while tokenizer.has_more_tokens():
                tokenizer.advance()
                tokenizer.output_line()
                #print(tokenizer.get_token_type)
                if tokenizer.token_type == 'KEYWORD':
                    pass
                    #print(f"<keyword> {tokenizer.get_key_word} </keyword>")
                    #ce.write_token('keyword', tokenizer.current_token)
                elif tokenizer.token_type == 'SYMBOL':
                    pass
                    #print(f"<symbol> {tokenizer.get_symbol} </symbol>")
                    #ce.write_token('symbol', tokenizer.current_token)
                elif tokenizer.token_type == 'INT_CONST':
                    pass
                    #print(f"<int> {tokenizer.get_int_val} </int>")
                    #ce.write_token('integerConstant', str(tokenizer.current_token))
                elif tokenizer.token_type == 'STRING_CONST':
                    pass
                    #print(f"<str> {tokenizer.get_string_val} </str>")
                    #ce.write_token('stringConstant', tokenizer.current_token)
                elif tokenizer.token_type == 'IDENTIFIER':
                    pass
                    #print(f"<ident> {tokenizer.get_identifier} </ident>")
                    #ce.write_token('identifier', tokenizer.current_token)
            tokenizer.output_close()
            #ce.close()


        #self.load_vm_codes()                                                    # 入力ファイルの内容をリストに取り込む
        #self.vm_tranlate()

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
        
        
    
            # 出力ファイル名を self.out_file に設定（ディレクトリ名.asm）
            #path_elements = file_path.split('/')
            #self.out_file = f"{file_path}/{path_elements[-1]}.asm"


class JackTokenizer(object):
    def __init__(self,jack_filename):
        self.jack_filename = jack_filename
        self.t_xml_filename = self.jack_filename.replace('.jack', 'T.xml')
        print(f' OutFile: {self.t_xml_filename}')
        self.output_file = open(self.t_xml_filename, 'w')
        self.write_init()

        self.jack_words = self.load_file(self.jack_filename) 
        print(self.jack_words)
        self.tokens = []
        self.token_types = []

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
        self.token_index = 0
        self.current_token = None
        self.current_token_type = None
        self.current_token_type_tag = None

    #######################
    ## API START ##########


    def has_more_tokens(self):
        return len(self.jack_words) > 0
    
    def advance(self):
        next_token=self.jack_words.popleft()

        # Case:symbol
        if next_token[0] in self.symbols:
            self.token_type = 'SYMBOL'
            self.current_token = next_token[0]
            if next_token[1:] :
                self.jack_words.appendleft(next_token[1:])
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
                    return

        # Case:stringContant
        if next_token[0] == '"':                                              # トークンの先頭が'"' の場合、"STRING_CONST" の開始と判断する
            self.token_type = 'STRING_CONST'
            current_string = next_token[1:]                                   # トークンの２文字目から最後まで current_string に代入
            full_string = ''                                                  # 最終的な文字列定数を保持するfull_stringを空文字列で初期化します
            while True:                                                       # 文字列定数の終端が見つかるまで無限ループを開始します
                for i, char in enumerate(current_string):                     # 現在の文字列の各文字に対して
                    if char == '"':                                           # 文字がダブルクォーテーションなら、文字列定数の終端と判断します
                        full_string += current_string[:i]                     # 終了クォートの前の文字を全文字列に追加します
                        if current_string[i+1:]:                              # 終了クォートの後に文字がある場合
                            self.jack_words.appendleft(current_string[i+1:])  # それらをjack_wordsの先頭に追加します
                        self.current_token = full_string.strip()              # 現在のトークンを、前後の空白を削除した全文字列として設定します
                        return                                                # 文字列定数が完全に処理されたので、関数を終了します
                full_string += current_string + ' '                           # 終了クォートが見つからない場合、現在の文字列とスペースを全文字列に追加します
                current_string = self.jack_words.popleft()                    # jack_wordsから次のトークンを取得し、ループを続行します

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
        return self.current_token

    @property
    def get_identifier(self):
        return self.current_token
    
    @property
    def get_string_val(self):
        return self.current_token
    
    ## API END ############
    #######################

    def write_init(self):
        print("<tokens>",file=self.output_file)

    def load_file(self, jack_filename: str) -> deque:
        
        print(f' - Loading {jack_filename}')
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
    
    def output_line(self):
        self.current_token_type_tag = self.token_tag_dict[self.token_type]
        #escaped_s = html.escape(s, quote=False)
        print(f"<{self.current_token_type_tag}> {html.escape(self.current_token, quote=False)} </{self.current_token_type_tag}>",file=self.output_file)

    def output_close(self):
        print("</tokens>",file=self.output_file)
        self.output_file.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 n2t_jack_analyzer.py <input_file> or <input_dir>")
        sys.exit(1)

    print("Jack Analyze Start")
    target_file_path  = sys.argv[1]

    vm_translator = N2TJackAnalyzer(target_file_path)
    vm_translator.run()

    print("Jack Analyze End")

