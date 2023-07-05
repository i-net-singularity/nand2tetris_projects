#!python
import sys,os
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
            tokenizer = JackTokenizer(jack_file)

            #ce = CompilationEngine(jack_file)
            while tokenizer.has_more_tokens():
                tokenizer.advance()
                #print(tokenizer.get_token_type)
                if tokenizer.token_type == 'KEYWORD':
                    print(f"<keyword> {tokenizer.get_key_word} </keyword>")
                    #ce.write_token('keyword', tokenizer.current_token)
                elif tokenizer.token_type == 'SYMBOL':
                    print(f"<symbol> {tokenizer.get_symbol} </symbol>")
                    #ce.write_token('symbol', tokenizer.current_token)
                elif tokenizer.token_type == 'INT_CONST':
                    print(f"<int> {tokenizer.get_int_val} </int>")
                #    pass
                    #ce.write_token('integerConstant', str(tokenizer.current_token))
                elif tokenizer.token_type == 'STRING_CONST':
                    print(f"<str> {tokenizer.get_string_val} </str>")
                #    pass
                    #ce.write_token('stringConstant', tokenizer.current_token)
                elif tokenizer.token_type == 'IDENTIFIER':
                    print(f"<ident> {tokenizer.get_identifier} </ident>")
                #    pass
                    #ce.write_token('identifier', tokenizer.current_token)
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

    def load_vm_codes(self):
        # 入力ファイルの内容をリストに取り込む
        for vm_files in self.jack_files :
            self.vm_codes[vm_files] = []
            with open(vm_files, 'r') as input_file:
                # 入力ファイルの内容を1行ずつ読む
                for line in input_file:
                    # 読み込んだ行をリストに追加
                    self.vm_codes[vm_files].append(line.strip())

    def vm_tranlate(self):
        """
        VMコードの変換
        """

        code_writer = CodeWriter(self.out_file)

        for vm_filepath, lines in self.vm_codes.items():
            print(f' File: {vm_filepath}')
            # 1行ずつVMコードを変換
            vm_parser = VMParser()
            vm_parser.vm_parse(lines)
            #vm_parser.increment()

            code_writer.write_assembly(vm_filepath,vm_parser.parsed_vm_codes)

        code_writer.close()

class JackTokenizer(object):
    def __init__(self,jack_filename):
        self.jack_filename = jack_filename
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
        
        self.token_index = 0
        self.current_token = None
        self.current_token_type = None

    #######################
    ## API START ##########
    def has_more_tokens(self):
        return len(self.jack_words) > 0
    
    def advance(self):
        next_token=self.jack_words.popleft()

        #print(next_token+" <= ## org-code ##")

        # Case:keyword
        if next_token in self.keywords_dict:
            self.token_type = 'KEYWORD'
            self.current_token = next_token
            return

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
            while True:
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

        # Case:identifier (上記のどのケースにも当てはまらない場合)
        self.token_type = 'IDENTIFIER'
        self.current_token = next_token
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


class VMParser(object):

    count=0
    @classmethod
    def increment(cls):
        cls.count += 1

    def __init__(self):
        # コマンドとコマンドタイプの対応辞書
        self.commands_dict = {
            'add'      : 'C_ARITHMETIC',
            'sub'      : 'C_ARITHMETIC',
            'neg'      : 'C_ARITHMETIC',
            'eq'       : 'C_ARITHMETIC',
            'gt'       : 'C_ARITHMETIC',
            'lt'       : 'C_ARITHMETIC',
            'and'      : 'C_ARITHMETIC',
            'or'       : 'C_ARITHMETIC',
            'not'      : 'C_ARITHMETIC',
            'push'     : 'C_PUSH',
            'pop'      : 'C_POP',
            'label'    : 'C_LABEL',
            'goto'     : 'C_GOTO',
            'if-goto'  : 'C_IF',
            'function' : 'C_FUNCTION',
            'return'   : 'C_RETURN',
            'call'     : 'C_CALL',
        }
    
    def vm_parse(self,lines):
        self.parsed_vm_codes=[]
        for line in lines:
            line = line.split(JACK_COMENT_1)[0].strip()
            if line :
                # ディクショナリにパース結果を設定
                command_tokens = line.split()
                command_type = self.commands_dict[command_tokens[0]]

                # arg1 の設定
                if command_type == 'C_ARITHMETIC':
                    arg1=command_tokens[0]
                elif command_type == 'C_RETURN':
                    arg1=None
                else:
                    arg1=command_tokens[1]

                # arg2 の設定
                if command_type == 'C_PUSH' or command_type == 'C_POP' or command_type == 'C_FUNCTION' or command_type == 'C_CALL':
                    arg2=command_tokens[2]
                else:
                    arg2=None

                parsed_line = {'command_type':command_type, 'arg1':arg1, 'arg2':arg2, 'vm_code' :line}

                # リストにディクショナリを追加
                self.parsed_vm_codes.append(parsed_line)

class CodeWriter(object):
    def __init__(self,out_file):

        """
        生成した機械語のファイル出力
        """

        # 条件分岐ラベルのカウント：条件分岐毎にインクリメントし固有のラベルを作成する
        self.label_count = 0
        # コールラベルのカウント：関数呼び出し毎にインクリメントし固有のラベルを作成する
        self.call_count = 0

        # メモリセグメントと実メモリのマッピング
        self.segment_dict = {
            'local'    : 'LCL',
            'argument' : 'ARG',
            'this'     : 'THIS',
            'that'     : 'THAT',
            'pointer'  : '3',
            'temp'     : '5',
            'static'   : 'R16',
            'constant' : 'undefined'    # 実メモリへの割り当てなし
        }

        print(f' OutFile: {asm_file}')
        self.output_file = open(asm_file, 'w')
        self.write_init()

    def write_assembly(self, vm_filepath,parsed_vm_codes):
        # VMファイル名を設定
        self.out_filename=vm_filepath.split('/')[-1].split('.')[0]
        # コマンドタイプに応じてアセンブリコードを出力
        for command in parsed_vm_codes:
            vm_code      = str(command['vm_code'])
            command_type = str(command['command_type'])
            arg1         = str(command['arg1'])
            arg2         = str(command['arg2'])

            self.output_line(f"{JACK_COMENT_1} {vm_code}")    # アセンブリの元となったVMコードを出力

            if   command_type == "C_ARITHMETIC" :
                self.write_arithmetic(arg1)

            elif command_type in ("C_PUSH","C_POP"):
                self.write_push_pop(command_type,arg1,arg2)

            elif command_type in ("C_LABEL"):
                self.write_label(arg1)
            elif command_type in ("C_GOTO"):
                self.write_goto(arg1)
            elif command_type in ("C_IF"):
                self.write_if(arg1)
            elif command_type in ("C_FUNCTION"):
                self.write_function(arg1,arg2)
            elif command_type in ("C_RETURN"):
                self.write_return()
            elif command_type in ("C_CALL"):
                self.write_call(arg1,arg2)
            else:
                pass

    def write_init(self):
        self.output_line("@256")
        self.output_line("D=A")
        self.output_line("@SP")
        self.output_line("M=D")
        self.write_call("Sys.init","0")

    def write_arithmetic(self,command):

        self.pop_stack_to_D()

        # unary operator
        if command == "neg":
            self.output_line("M=-D") 

        elif command == "not":
            self.output_line("M=!D") 

        # binary operator
        elif command in ("add","sub","and","or"):
            self.sp_decrement()
            self.output_line("A=M")
            if   command == "add":
                self.output_line("M=D+M") 
            elif command == "sub":
                self.output_line("M=M-D")
            elif command == "and":
                self.output_line("M=D&M")
            elif command == "or":
                self.output_line("M=D|M")

        # Comparison operator
        elif command in ("eq","gt","lt"):
            self.sp_decrement()
            self.output_line("A=M")
            self.output_line("D=M-D")

            label_true = f"LABEL{str(self.label_count).zfill(5)}_TRUE"
            label_end  = f"LABEL{str(self.label_count).zfill(5)}_END"

            self.output_line("@" + label_true)
            if command == "eq":
                self.output_line("D;JEQ")
            elif command == "gt":
                self.output_line("D;JGT")
            elif command == "lt":
                self.output_line("D;JLT")

            # if false
            self.set_A_to_stack()
            self.output_line(f"M={VM_FALSE}") # set false valueW
            self.output_line(f"@{label_end}")
            self.output_line("0;JMP")
            
            # if true
            self.output_line(f"({label_true})")
            self.set_A_to_stack()
            self.output_line(f"M={VM_TRUE}") #set true value (-1 = 0xffff)
            self.output_line(f"({label_end})")
            self.label_count += 1

        self.sp_increment()

    def write_push_pop(self,command_type,segment,index):
        '''
        command_type: C_PUSH or C_POP
        segment: メモリセグメント
        index  : インデックス
        '''

        # (1) セグメントに対応したメモリアドレスを取得する
        segment_address = self.segment_dict[segment]

        # (2) セグメントとインデックスからPUSH/POP位置を計算する
        if(segment == "constant"):
            self.output_line(f"@{index}")
        else:
            if(segment in ("local","argument","this","that")):
                self.output_line(f"@{segment_address}")
                self.output_line("D=M")
                self.output_line(f"@{index}")
                self.output_line("A=D+A")

            elif(segment in ("pointer","temp")):
                self.output_line(f"@R{str(int(segment_address) + int(index))}")

            elif(segment == "static"):
                self.output_line(f"@{self.out_filename}.{index}")
 
        # (3) PUSH/POPを実行する
        if(command_type == "C_PUSH"):
            if(segment == "constant"):
                 self.output_line("D=A")    # 定数(constant)の場合はAレジスタに値をセット
            else:
                 self.output_line("D=M")    # 定数以外はメモリから値を取得　(メモリアドレスは(2)で計算済み)
            self.push_D_to_stack()

        elif(command_type == "C_POP"):
             self.output_line("D=A")
             self.output_line("@R13")
             self.output_line("M=D")     # R13にPOP先のアドレスを保存
             self.pop_stack_to_D()
             self.output_line("@R13")
             self.output_line("A=M")
             self.output_line("M=D")

    def write_label(self,label):
        self.output_line(f"({self.out_filename}${label})")
    
    def write_goto(self,label):
        self.output_line(f"@{self.out_filename}${label}")
        self.output_line(f"0;JMP")

    def write_if(self,label):
        self.pop_stack_to_D()
        self.output_line(f"@{self.out_filename}${label}")
        self.output_line(f"D;JNE")

    def write_function(self,function_name,num_locals):
        self.output_line(f"({function_name})")
        for i in range(int(num_locals)):
            self.output_line("D=0")
            self.push_D_to_stack()

    def write_return(self):
        #FRAME = LCL:
        #「FRAME」は仮想的なポインタで、現在の「LCL」（Local ポインタ）の値を指す。
        FRAME="R13"
        self.output_line("@LCL")
        self.output_line("D=M")
        self.output_line(f"@{FRAME}")
        self.output_line("M=D")

        #RET = *(FRAME-5):
        #「RET」（Return）は仮想的なポインタで、「FRAME」から5引いた値にあるデータ（現在の関数が呼び出された場所）を指す。
        RET="R14"
        self.output_line(f"@{FRAME}")
        self.output_line("D=M")
        self.output_line("@5")
        self.output_line("A=D-A")
        self.output_line("D=M")
        self.output_line(f"@{RET}")
        self.output_line("M=D")

        #*ARG = pop():
        #スタックから一つ値を取り出し（pop）、それを「ARG」が指すアドレスに格納する。これにより関数の返り値を設定する。
        self.pop_stack_to_D()
        self.output_line("@ARG")
        self.output_line("A=M")
        self.output_line("M=D")

        #SP = ARG+1:
        #「SP」（Stack Pointer）を「ARG」の値に1を足した位置に移動する。これによりスタックポインタを返り値のすぐ上に移動させる。
        self.output_line("@ARG")
        self.output_line("D=M")
        self.output_line("@SP")
        self.output_line("M=D+1")

        #THAT = *(FRAME-1), THIS = *(FRAME-2), ARG = *(FRAME-3), LCL = *(FRAME-4):
        #「FRAME」から1～4引いた各値にあるデータを、それぞれ「THAT」、「THIS」、「ARG」、「LCL」に設定する。これにより呼び出し元の関数の状態を復元する。
        offset=1
        for symbol in ("THAT","THIS","ARG","LCL"):
            self.output_line(f"@{FRAME}")
            self.output_line("D=M")
            self.output_line(f"@{offset}")
            self.output_line("A=D-A")
            self.output_line("D=M")
            self.output_line(f"@{symbol}")
            self.output_line("M=D")
            offset += 1

        #goto RET:
        #「RET」が指すアドレスへジャンプする。これにより戻り先のアドレスへ制御を移す。
        self.output_line(f"@{RET}")
        self.output_line("A=M")
        self.output_line("0;JMP")
        
    def write_call(self,function_name,num_args):
        #コールラベル生成
        return_address_label=(f"{function_name}RET{str(self.call_count)}")
        self.call_count+=1

        #push return-address //（ 以下のラベル宣言を用いる）
        self.output_line(f"@{return_address_label}")
        self.output_line("D=A")
        self.push_D_to_stack()

        #push LCL            // 関数の呼び出し側のLCLを格納する
        #push ARG            // 関数の呼び出し側のARGを格納する
        #push THIS           // 関数の呼び出し側のTHISを格納する
        #push THAT           // 関数の呼び出し側のTHATを格納する
        for symbol in ("LCL","ARG","THIS","THAT"):
            self.output_line(f"@{symbol}")
            self.output_line("D=M")
            self.push_D_to_stack()

        #ARG = SP-n-5        // ARGを別の場所に移す（n＝引数の数）
        self.output_line("@SP")
        self.output_line("D=M")
        self.output_line(f"@{int(num_args)+5}")
        self.output_line("D=D-A")
        self.output_line("@ARG")
        self.output_line("M=D")

        #LCL = SP            // LCLを別の場所に移す
        self.output_line("@SP")
        self.output_line("D=M")
        self.output_line("@LCL")
        self.output_line("M=D")

        #goto f              // 制御を移す
        self.output_line(f"@{function_name}")
        self.output_line("0;JMP")

        #(return-address)    // リターンアドレスのためのラベルを宣言する
        self.output_line(f"({return_address_label})")

    def push_D_to_stack(self):
        self.set_A_to_stack()
        self.output_line("M=D") # Write data to top of stack
        self.sp_increment()     # Increment SP

    def pop_stack_to_D(self):
        self.sp_decrement()
        self.output_line("A=M")
        self.output_line("D=M")

    def set_A_to_stack(self):
        self.output_line("@SP") # Get current stack pointer
        self.output_line("A=M") # Set address to current stack pointer

    def sp_increment(self):
        self.output_line("@SP")
        self.output_line("M=M+1")

    def sp_decrement(self):
        self.output_line("@SP")
        self.output_line("M=M-1")

    def output_line(self,mnemonic):
        print(mnemonic,file=self.output_file)

    def close(self):
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

