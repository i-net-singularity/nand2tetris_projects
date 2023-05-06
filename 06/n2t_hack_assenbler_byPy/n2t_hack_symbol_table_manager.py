# ------------------------------------------------------------------------------
# Symbol_Table_Manager Class
# ------------------------------------------------------------------------------
class HackSymbolTableManager:
    """
    シンボルテーブルを管理するクラス
    """
    def __init__(self):
        """
        シンボルテーブルを初期化する
        """
        self.symbol_table = {
            "pre_defined" : {
                'SP'  : 0,
                'LCL' : 1,
                'ARG' : 2,
                'THIS': 3,
                'THAT': 4,
                'R0'  : 0,
                'R1'  : 1,
                'R2'  : 2,
                'R3'  : 3,
                'R4'  : 4,
                'R5'  : 5,
                'R6'  : 6,
                'R7'  : 7,
                'R8'  : 8,
                'R9'  : 9,
                'R10' : 10,
                'R11' : 11,
                'R12' : 12,
                'R13' : 13,
                'R14' : 14,
                'R15' : 15,
                'SCREEN' : 16384,
                'KBD' : 24576
            },
            "label_defined"  :{},
            "variable_defined" :{}
        }

    def add_l_symbol(self, symbol,line_number):
        """
        ラベルシンボルを追加する
        """
        # 未定義のラベルシンボルの場合は追加する
        if self.symbol_table["label_defined"].get(symbol)    is None :
            self.symbol_table["label_defined"][symbol] = line_number

    def add_a_symbol(self, symbol):
        """
        Aコマンドのシンボルを追加する
        """
        # 未定義のシンボルの場合、シンボルテーブルに追加する
        if self.symbol_table["pre_defined"].get(symbol)      is None and \
           self.symbol_table["label_defined"].get(symbol)    is None and \
           self.symbol_table["variable_defined"].get(symbol) is None :
            # 独自定義シンボルテーブルに追加（16から始まる）
            address = len(self.symbol_table["variable_defined"])+16
            self.symbol_table["variable_defined"][symbol] = address

    def get_address(self, symbol):
        """
        シンボルに結びつけられたアドレスを返す
        """
        address = self.symbol_table["pre_defined"].get(symbol)

        if address is None:
            address = self.symbol_table["label_defined"].get(symbol)

        if address is None:
            address = self.symbol_table["variable_defined"].get(symbol)

        return address

    def show_dict_all(self):
        print("show_dict_all start")
        print(self.symbol_table["label_defined"])
        print(self.symbol_table["variable_defined"])
        print("show_dict_all end")