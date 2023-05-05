#!python
import sys
import re
import json

from typing import List, Dict
from collections import namedtuple
from typing import Tuple

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

    converted_asm_codes=asm_code_converter(parsed_asm_codes)
    for line in converted_asm_codes:
        print(line)

    # 出力ファイルを書き込みモードで開く
    #with open(output_file_name, 'w') as output_file:
    #    # リストに保持した内容を1行ずつ出力ファイルに書き込む
        #for line in parsed_asm_codes:
            #output_file.write(line.'cmdType' + '\n')
    with open(output_file_name, 'w') as output_file:
        for item in converted_asm_codes:
            output_file.write(item)
            output_file.write("\n")  # 各ディクショナリの間に空行を挿入

# ------------------------------------------------------------------------------
# Parser 関数
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

    for line in asm_codes:

        # コメントを除去する
        line = line.split('//')[0]

        # 先頭と末尾の空白文字を削除する
        line = line.strip()

        # 空白行を除去する
        if line:
            
            # commandType に応じてパースする
            if re.match('^@', line):       # A_COMMAND
                cmdType = 'A'
                symbol= re.findall(a_cmd_pattern, line)[0]
                dest=None
                comp=None
                jump=None

            elif  re.match('^\(', line):   # L_COMMAND
                cmdType = 'L'
                symbol= re.findall(l_cmd_pattern, line)[0]
                dest=None
                comp=None
                jump=None

            else:                           # C_COMMAND
                cmdType = 'C'
                symbol=None

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
          },
        "jump":{
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
        if line['cmdType'] == 'A':
            aCmdValueConvedToBin = bin(int(line['symbol']))[2:].zfill(15)

            converted_asm_codes.append("0" + aCmdValueConvedToBin)

        elif line['cmdType'] == 'C':
            dest_code = machine_codes_dict['dest'][line['dest']]
            comp_code = machine_codes_dict['comp'][line['comp']]
            jump_code = machine_codes_dict['jump'][line['jump']]

            converted_asm_codes.append("111" + comp_code + dest_code + jump_code)

    return converted_asm_codes



# ------------------------------------------------------------------------------
# SymbolTable
# ------------------------------------------------------------------------------



if __name__ == '__main__':
    main()
    

# 


# 6.3.3 シンボルを含まないプログラムのためのアセンブラ
# アセンブラを作るにあたって、次の2 段階の手順で作ることを推奨する。最初の段
# 階として、シンボルを用いないアセンブリプログラムを対象に、それを変換するため
# のアセンブラを書く。これは先ほど説明したParser とCode モジュールを用いて行
# うことができる。そして次の段階で、シンボルを扱えるように先のアセンブラを拡張
# する。シンボルの対応については次節で説明する。
# 最初の「シンボルフリーなアセンブラ」の段階では、Prog.asm にはシンボルが含
# まれていないことを条件とする。これはつまり、次のふたつの条件を満たすというこ
# とである。
# ● すべての@Xxx というタイプのアドレスコマンドにおいて、Xxx は10 進数の
# 数値であり、シンボルでない。
# ● 入力ファイルには(Xxx) のようなラベル宣言のコマンドが含まれない。
# 「シンボルフリーなアセンブラ」は次のように実装することができる。まず
# Prog.hack という名前の出力ファイルを開き、続いて、与えられたProg.asm
# ファイルの各行（アセンブリの命令）をひとつずつ処理していく。C 命令に対しては、
# 各命令フィールドをバイナリコードへと変換し、それらを連結させて16 ビットの命令
# を構成する。そして、この16 ビット命令をProg.hack ファイルへ書き込む。@Xxx
# というタイプのA 命令に対しては、Parse モジュールから返された10 進数の数値を
# バイナリ表現へ変換し、その16 ビットのワードをProg.hack ファイルへ書き込む。

# 6.3.4 SymbolTable モジュール
# Hack 命令はシンボルを含むため、変換処理のどこかで、シンボルは実際のアドレス
# 126 6 章アセンブラへと解決されなければならない。この処理にはシンボルテーブルを用いる。シンボル
# テーブルはシンボルとその内容（Hack の場合、RAM またはROM のアドレス）の対応表が保持される。
# ほとんどのプログラミング言語で、そのようなデータ構造は標準ライブラリとして用意されているため、ゼロから実装する必要はないだろう。ここでは表6-3 に示すAPI を実装することを推奨する。
# 表6-3 SymbolTable モジュールのAPI
# ルーチン引数戻り値機能
# コンストラクタ/
# 初期化
# － － 空のシンボルテーブルを作成する
# addEntry symbol（文字列）、
# address（整数）
# － テーブルに(symbol,adress) のペアを追加する
# contains symbol（文字列） ブール値シンボルテーブルは与えられたsymbolを含むか？
# getAddress symbol（文字列） 整数symbol に結びつけられたアドレスを返す

# ----------------------
# 入力ファイルを読み込む
#with open(input_file_name, 'r') as input_file:
#    # 出力ファイルを書き込みモードで開く
#    with open(output_file_name, 'w') as output_file:
#        # 入力ファイルの内容を1行ずつ読む
#        for line in input_file:
#            # 読み込んだ行をそのまま出力ファイルに書き込む
#            output_file.write(line)
