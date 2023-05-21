#!python
import sys,os
from typing import List,Dict

VM_COMENT = '//'

class N2THackVMTranslator(object):

    def __init__(self, target_file_path: str):
        
        # 入力ファイル名と出力ファイル名を保持する変数を初期化
        self.vm_files = []
        self.asm_file = None

        self.vm_codes = {}              # ファイルごとに1行ごとのVMコードを格納する
        self.parsed_vm_codes = {}       # ファイルごとにVMコードのパース結果を格納する
        self.asm_codes = []

        #self.symbol_table_manager = HackSymbolTableManager()

    def run(self):
        self.prepare_file_paths(target_file_path)                               # 入力ファイル名と出力ファイル名を設定
        self.load_vm_codes()                                                    # 入力ファイルの内容をリストに取り込む
        self.vm_tranlate()
        #self.convert_asm_codes()
        #self.write_machine_codes()
        pass

    def prepare_file_paths(self, file_path):
        print(" file_path = " + file_path)

        if '.vm' in file_path:
            # --------------------------
            # ファイル指定の場合
            # --------------------------
            # 入力ファイル名を self.vm_files に設定
            self.vm_files = [file_path]
            # 出力ファイル名を self.asm_file に設定（拡張子を '.vm' から '.asm' に置換する）
            self.asm_file = file_path.replace('.vm', '.asm')

        else:
            # --------------------------
            # ディレクトリ指定の場合
            # --------------------------
            # 最後の '/' を削除
            file_path = file_path.rstrip('/')

            # os.walk を使ってディレクトリパス、ディレクトリ名、ファイル名を取得
            dirpath, dirnames, filenames = next(os.walk(file_path), ([], [], []))

            # '.vm' を含むファイルのみ対象とする
            vm_files = [filename for filename in filenames if '.vm' in filename]

            # 入力ファイル名を self.vm_files に設定（複数ファイルを想定）
            self.vm_files = [f"{file_path}/{vm_file}" for vm_file in vm_files]

            # 出力ファイル名を self.asm_file に設定（ディレクトリ名.asm）
            path_elements = file_path.split('/')
            self.asm_file = f"{file_path}/{path_elements[-1]}.asm"

    def load_vm_codes(self):
        # 入力ファイルの内容をリストに取り込む
        for vm_files in self.vm_files :
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

        code_writer = CodeWriter(self.asm_file)

        for filepath, lines in self.vm_codes.items():
            print(f' File: {filepath}')
            # 1行ずつVMコードを変換
            vm_parser = VMParser()
            vm_parser.vm_parse(lines)
            #vm_parser.increment()

            code_writer.write_assembly(vm_parser.parsed_vm_codes)

            #for line in vm_parser.parsed_vm_codes:
            #    print(f'{vm_parser.count,line}')
            print('---')  # 各ファイルが終わったことを示すための区切り線

        code_writer.close()

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
        }
    
    def vm_parse(self,lines):
        self.parsed_vm_codes=[]
        for line in lines:
            line = line.split(VM_COMENT)[0].strip()
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
    def __init__(self,asm_file):
        """
        生成した機械語のファイル出力
        """
        print(f' OutFile: {asm_file}')
        self.output_file = open(asm_file, 'w')

        # メモリセグメントと実メモリのマッピング
        self.segment_dict = {
            'local'    : 'LCL',
            'argument' : 'ARG',
            'this'     : 'THIS',
            'that'     : 'THAT',
            'pointer'  : 'R3',
            'temp'     : 'R5',
            'static'   : 'R16',
        }

        # ラベルのカウント：条件分岐毎にインクリメントし固有のラベルを作成する
        self.label_count = 1

    def write_assembly(self, parsed_vm_codes):
        # コマンドタイプに応じてアセンブリコードを出力
        for command in parsed_vm_codes:
            vm_code      = str(command['vm_code'])
            command_type = str(command['command_type'])
            arg1         = str(command['arg1'])
            arg2         = str(command['arg2'])

            self.output_line("// " + vm_code)    # アセンブリの元となったVMコードを出力

            if   command_type == "C_ARITHMETIC" :
                self.write_arithmetic(arg1,arg2)

            elif command_type == "C_PUSH":
                self.write_push_pop("C_PUSH",arg1,arg2)
            elif command_type == "C_POP":
                self.write_push_pop("C_POP" ,arg1,arg2)
            else:
                pass
        
    def write_arithmetic(self,arg1,arg2):

        self.pop_stack_to_D()

        # unary operator
        if arg1 in ("neg","not"):

            if arg1 == "neg":
                self.output_line("M=-D") 

            if arg1 == "not":
                self.output_line("M=!D") 

        # binary operator
        elif arg1 in ("add","sub","and","or"):
            self.sp_decrement()
            self.output_line("A=M")
            if   arg1 == "add":
                self.output_line("M=D+M") 
            elif arg1 == "sub":
                self.output_line("M=M-D")
            elif arg1 == "and":
                self.output_line("M=D&M")
            elif arg1 == "or":
                self.output_line("M=D|M")

        elif arg1 in ("eq","gt","lt"):
            self.sp_decrement()
            self.output_line("A=M")
            self.output_line("D=M-D")

            # Comparison part
            label_true  = "LABEL" + str(self.label_count).zfill(5) + "_TRUE"
            label_end   = "LABEL" + str(self.label_count).zfill(5) + "_END"

            self.output_line("@" + label_true)
            if arg1 == "eq":
                self.output_line("D;JEQ")
            elif arg1 == "gt":
                self.output_line("D;JGT")
            elif arg1 == "lt":
                self.output_line("D;JLT")

            # if false
            self.output_line("@SP")
            self.output_line("A=M")
            self.output_line("M=0") # set false value
            self.output_line("@" + label_end)
            self.output_line("0;JMP")
            
            # if true
            self.output_line("(" + label_true + ")")
            self.output_line("@SP")
            self.output_line("A=M")
            self.output_line("M=-1") #set true value (-1 = 0xffff)

            self.output_line("(" + label_end + ")")
            self.label_count += 1

        self.sp_increment()

    def write_push_pop(self,command_type,arg1,arg2):
        # memo address 解決必要あり
        if(command_type == "C_PUSH"):
            if(arg1 == "constant"):
                self.output_line("@" + arg2)
                self.output_line("D=A")
                self.push_D_to_stack()

        if(command_type == "C_POP"):
            self.output_line("@" + arg2)

    def push_D_to_stack(self):
        '''Push from D onto top of stack, increment @SP'''
        self.output_line("@SP") # Get current stack pointer
        self.output_line("A=M") # Set address to current stack pointer
        self.output_line("M=D") # Write data to top of stack
        self.sp_increment()     # Increment SP

    def pop_stack_to_D(self):
        '''Decrement @SP, pop from top of stack onto D'''
        self.sp_decrement()
        self.output_line("A=M")
        self.output_line("D=M")

    def sp_increment(self):
        self.output_line("@SP")
        self.output_line("M=M+1")

    def sp_decrement(self):
        self.output_line("@SP")
        self.output_line("M=M-1")

    #def push_D_to_stack(self):
    #    '''Push from D onto top of stack, increment @SP'''
    #    self.write('@SP') # Get current stack pointer
    #    self.write('A=M') # Set address to current stack pointer
    #    self.write('M=D') # Write data to top of stack
    #    self.write('@SP') # Increment SP
    #    self.write('M=M+1')

    #def pop_stack_to_D(self):
    #    '''Decrement @SP, pop from top of stack onto D'''
    #    self.write('@SP')
    #    self.write('M=M-1') # Decrement SP
    #    self.write('A=M') # Set address to current stack pointer
    #    self.write('D=M') # Get data from top of stack

    def output_line(self,mnemonic):
        print(mnemonic,file=self.output_file)

    def close(self):
        self.output_file.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 n2t_hack_vm_translator.py <input_file> or <input_dir>")
        sys.exit(1)

    print("VM Translate Start")
    target_file_path  = sys.argv[1]

    vm_translator = N2THackVMTranslator(target_file_path)
    vm_translator.run()

    print("VM Translate End")

