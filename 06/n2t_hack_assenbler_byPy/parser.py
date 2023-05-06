from typing import List,Dict
import re

class Parser:
    """
    Hack仕様のアセンブリ言語をパースするクラス
    """
    def __init__(self):
        # パース済みアセンブリコードを格納するリスト
        self.parsed_asm_codes = [] 

        # マッチパターン
        a_cmd_pattern = r'^@(.*)'
        l_cmd_pattern = r'\((.*)\)'

    def parse_assembly(self,asm_codes: List[str]) -> List[Dict]:
        """
        Parse a list of assembly codes into a list of dictionaries containing information about the commands.
        
        Args:
            asm_codes (List[str]): A list of assembly code strings.
        
        Returns:
            List[Dict]: A list of dictionaries containing parsed assembly code information.
        """

        # 1 : L_COMMAND の シンボルテーブルを作成する
        ac_cmd_line_number= 0
        for line in asm_codes:
            # コメントを除去する
            line = line.split('//')[0]

            # 先頭と末尾の空白文字を削除する
            line = line.strip()

            # 空白行を除去する
            if line:
                if  re.match(self.l_cmd_pattern, line):   # L_COMMAND
                    symbol= re.findall(self.l_cmd_pattern, line)[0]
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