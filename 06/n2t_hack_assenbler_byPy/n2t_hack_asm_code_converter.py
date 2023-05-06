import sys

from typing import List,Dict
from n2t_hack_symbol_table_manager import HackSymbolTableManager

class HackAsmCodeConverter:
    """
    ニーモニックをバイナリコードに変換するクラス
    ルーチン引数      戻り値   機能
    dest ニーモニック（文字列）3 ビットdest ニーモニックのバイナリコードを返す
    comp ニーモニック（文字列）7 ビットcomp ニーモニックのバイナリコードを返す
    jump ニーモニック（文字列）3 ビットjump ニーモニックのバイナリコードを返す
    """
    def __init__(self):
        # ニーモニックとバイナリコードの対応
        self.machine_codes_dict={
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

        self.converted_asm_codes = []

    def convert(self, parsed_asm_codes,symbol_table_manager:HackSymbolTableManager):
        # ニーモニックをバイナリコードに変換する処理
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
                    self.converted_asm_codes.append("0" + a_cmd_val_to_bin)

                # C_COMMAND
                elif line['cmdType'] == 'C':

                    # ニーモニックを対応するバイナリコードに変換する
                    # ニーモニックに対応するバイナリコードが存在しない場合はエラーとする
                    try:
                        dest_code = self.machine_codes_dict['dest'][line['dest']]
                    except KeyError:
                        print("Error: dest is None -> " + line["code"])
                        sys.exit(1)
                    
                    try:
                        comp_code = self.machine_codes_dict['comp'][line['comp']]
                    except KeyError:
                        print("Error: comp is None -> " + line["code"])
                        sys.exit(1)
                    try:
                        jump_code = self.machine_codes_dict['jump'][line['jump']]
                    except KeyError:
                        print("Error: jump is None -> " + line["code"])
                        sys.exit(1)

                    # コードをリストに追加する
                    self.converted_asm_codes.append("111" + comp_code + dest_code + jump_code)

            return self.converted_asm_codes
