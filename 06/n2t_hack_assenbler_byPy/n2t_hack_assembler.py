#!python

import sys

from n2t_hack_symbol_table_manager import HackSymbolTableManager
from n2t_hack_asm_parser           import HackAsmParser
from n2t_hack_asm_code_converter   import HackAsmCodeConverter

class N2THackAssembler:
    def __init__(self, input_file_name: str, output_file_name: str):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.asm_codes = []
        self.parsed_asm_codes = []
        self.converted_asm_codes = []

        #シンボルテーブル初期化
        self.symbol_table_manager = HackSymbolTableManager()

    def run(self):
        self.load_asm_codes()
        self.parse_asm_codes()
        self.convert_asm_codes()
        self.write_machine_codes()

    def load_asm_codes(self):
        # 入力ファイルの内容をリストに取り込む
        with open(self.input_file_name, 'r') as input_file:
            # 入力ファイルの内容を1行ずつ読む
            for line in input_file:
                # 読み込んだ行をリストに追加
                self.asm_codes.append(line.strip())

    def parse_asm_codes(self):
        """
        アセンブリコードのパース
        """
        # AsmParser インスタンスを作成
        asm_parser = HackAsmParser()
        # AsmParser.parse を使用してアセンブリコードをパース
        self.parsed_asm_codes = asm_parser.parse_assembly(self.asm_codes, self.symbol_table_manager)

    def convert_asm_codes(self):
        """
        アセンブリコードの変換
        """
        # AsmParser インスタンスを作成
        asm_code_converter = HackAsmCodeConverter()
        # AsmParser.parse を使用してアセンブリコードをパース
        self.converted_asm_codes = asm_code_converter.convert(self.parsed_asm_codes, self.symbol_table_manager)

    def write_machine_codes(self):
        """
        生成した機械語のファイル出力
        """
        with open(output_file_name, 'w') as output_file:
            for machine_code in self.converted_asm_codes:
                output_file.write(machine_code + "\n")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 n2t_hack_assembler.py <input_file> <output_file>")
        sys.exit(1)

    input_file_name  = sys.argv[1]
    output_file_name = sys.argv[2]

    assembler = N2THackAssembler(input_file_name, output_file_name)
    assembler.run()