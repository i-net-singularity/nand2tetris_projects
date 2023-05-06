#!python
import sys
import re
from typing import List, Dict
#import json
from symbol_table_manager import SymbolTableManager



# ------------------------------------------------------------------------------
# Symbol Table 生成
# ------------------------------------------------------------------------------
symbol_table_manager = SymbolTableManager()

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main():
    # コマンドライン引数の数をチェック
    if len(sys.argv) != 3:
        print("Usage: python3 assembler.py <input_file> <output_file>")
        sys.exit(1)

    # 入力ファイル名と出力ファイル名をコマンドライン引数から取得
    input_file_name  = sys.argv[1]
    output_file_name = sys.argv[2]

    # 入力ファイルの内容を保持するリスト
    asm_codes = []
    # パース結果
    parsed_asm_codes = []

    # 入力ファイルをリストに取り込む
    with open(input_file_name, 'r') as input_file:
        # 入力ファイルの内容を1行ずつ読む
        for line in input_file:
            # 読み込んだ行をリストに追加
            asm_codes.append(line.strip())

    parsed_asm_codes=asm_parser(asm_codes)
    #for line in parsed_asm_codes:
    #    print(line)

    #symbol_table_manager.show_dict_all()

    converted_asm_codes=asm_code_converter(parsed_asm_codes)
    #for line in converted_asm_codes:
    #    print(line)

    # 出力ファイルを書き込みモードで開く
    # リストに保持した内容を1行ずつ出力ファイルに書き込む
    with open(output_file_name, 'w') as output_file:
        for machine_code in converted_asm_codes:
            output_file.write(machine_code + "\n")

# ------------------------------------------------------------------------------
# Parser
# ------------------------------------------------------------------------------
def asm_parser(asm_codes: List[str]) -> List[Dict]:
    """
    Parse a list of assembly codes into a list of dictionaries containing information about the commands.
    
    Args:
        asm_codes (List[str]): A list of assembly code strings.
    
    Returns:
        List[Dict]: A list of dictionaries containing parsed assembly code information.
    """

    parsed_asm_codes = [] # パース済みアセンブリコードを格納するリスト
    # 名前付きタプルでデータセットを定義
    #'DataSet', ['cmdType', 'symbol', 'dest', 'comp', 'jump']

    a_cmd_pattern = r'^@(.*)'
    l_cmd_pattern = r'\((.*)\)'

    # 1 : L_COMMAND の シンボルテーブルを作成する
    ac_cmd_line_number= 0
    for line in asm_codes:
        # コメントを除去する
        line = line.split('//')[0]

        # 先頭と末尾の空白文字を削除する
        line = line.strip()

        # 空白行を除去する
        if line:
            if  re.match(l_cmd_pattern, line):   # L_COMMAND
                symbol= re.findall(l_cmd_pattern, line)[0]
                symbol_table_manager.add_l_symbol(symbol,ac_cmd_line_number)
            else:
                ac_cmd_line_number += 1

    # 2 : A_COMMAND/C_COMMAND をパースする（A_COMMANDはシンボルテーブルへの登録も実施する）
    for line in asm_codes:

        # パース結果初期化
        symbol = None
        dest   = None
        comp   = None
        jump   = None

        # コメントを除去する
        line = line.split('//')[0]

        # 先頭と末尾の空白文字を削除する
        line = line.strip()

        # 空白行を除去する
        if line:

            # commandType に応じてパースする
            if  re.match(l_cmd_pattern, line):   # L_COMMAND
                cmdType = 'L'

            elif re.match(a_cmd_pattern, line):       # A_COMMAND
                cmdType = 'A'
                symbol= re.findall(a_cmd_pattern, line)[0]

                # symbol が数値以外で構成されている場合、シンボルテーブルに登録する
                if not symbol.isdecimal():
                    symbol_table_manager.add_a_symbol(symbol)

            else:                           # C_COMMAND
                cmdType = 'C'

                # dest 取得
                if '=' in line:
                    dest = line.split('=')[0]
                    remaining_code = line.split('=')[1]
                else:
                    remaining_code = line.split('=')[0]

                # comp, jump 取得
                if ';' in remaining_code:
                    comp = remaining_code.split(';')[0]
                    jump = remaining_code.split(';')[1]
                else:
                    comp = remaining_code.split(';')[0]

            # ディクショナリにパース結果を設定
            data_dict = {'cmdType':cmdType, 'symbol':symbol, 'dest':dest, 'comp':comp, 'jump':jump, 'code' :line}

            # リストにディクショナリを追加
            parsed_asm_codes.append(data_dict)
        
    return parsed_asm_codes

# ------------------------------------------------------------------------------
# Code
# ------------------------------------------------------------------------------
def asm_code_converter(parsed_asm_codes: List[Dict]) -> List[Dict]:
    """
    アセンブリ言語のニーモニックをバイナリコードへ変換する
    # ルーチン引数      戻り値   機能
    # dest ニーモニック（文字列）3 ビットdest ニーモニックのバイナリコードを返す
    # comp ニーモニック（文字列）7 ビットcomp ニーモニックのバイナリコードを返す
    # jump ニーモニック（文字列）3 ビットjump ニーモニックのバイナリコードを返す
    """

    # ニーモニックとバイナリコードの対応
    machine_codes_dict={
        "dest":{
           None   :'000'
          ,'M'    :'001'
          ,'D'    :'010'
          ,'MD'   :'011'
          ,'A'    :'100'
          ,'AM'   :'101'
          ,'AD'   :'110'
          ,'AMD'  :'111'
          }
       ,"comp":{
           '0'    :'0101010'
          ,'1'    :'0111111'
          ,'-1'   :'0111010'
          ,'D'    :'0001100'
          ,'A'    :'0110000'
          ,'!D'   :'0001101'
          ,'!A'   :'0110001'
          ,'-D'   :'0001111'
          ,'-A'   :'0110011'
          ,'D+1'  :'0011111'
          ,'A+1'  :'0110111'
          ,'D-1'  :'0001110'
          ,'A-1'  :'0110010'
          ,'D+A'  :'0000010'
          ,'D-A'  :'0010011'
          ,'A-D'  :'0000111'
          ,'D&A'  :'0000000'
          ,'D|A'  :'0010101'
          ,'M'    :'1110000'
          ,'!M'   :'1110001'
          ,'-M'   :'1110011'
          ,'M+1'  :'1110111'
          ,'M-1'  :'1110010'
          ,'D+M'  :'1000010'
          ,'D-M'  :'1010011'
          ,'M-D'  :'1000111'
          ,'D&M'  :'1000000'
          ,'D|M'  :'1010101'
          }
       ,"jump":{
           None   :'000'
          ,'JGT'  :'001'
          ,'JEQ'  :'010'
          ,'JGE'  :'011'
          ,'JLT'  :'100'
          ,'JNE'  :'101'
          ,'JLE'  :'110'
          ,'JMP'  :'111'
          }
    }

    converted_asm_codes = []

    for line in parsed_asm_codes:
        # A_COMMAND
        if line['cmdType'] == 'A':

            # symbol が数値の場合、そのまま「a_cmd_val」に設定する
            if line['symbol'].isdecimal():
                a_cmd_val = line['symbol']

            # symbol が数値以外の場合、シンボルテーブルからアドレスを取得し「a_cmd_val」に設定する
            else:
                a_cmd_val = symbol_table_manager.get_address(line['symbol'])

            # 10進数を2進数に変換する(0bは除き、15ビットで0埋め)
            a_cmd_val_to_bin = bin(int(a_cmd_val))[2:].zfill(15)

            # コードをリストに追加する
            converted_asm_codes.append("0" + a_cmd_val_to_bin)

        # C_COMMAND
        elif line['cmdType'] == 'C':

            # ニーモニックを対応するバイナリコードに変換する
            # ニーモニックに対応するバイナリコードが存在しない場合はエラーとする
            try:
                dest_code = machine_codes_dict['dest'][line['dest']]
            except KeyError:
                print("Error: dest is None -> " + line["code"])
                sys.exit(1)
            
            try:
                comp_code = machine_codes_dict['comp'][line['comp']]
            except KeyError:
                print("Error: comp is None -> " + line["code"])
                sys.exit(1)
            try:
                jump_code = machine_codes_dict['jump'][line['jump']]
            except KeyError:
                print("Error: jump is None -> " + line["code"])
                sys.exit(1)

            # コードをリストに追加する
            converted_asm_codes.append("111" + comp_code + dest_code + jump_code)

    return converted_asm_codes

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
