from typing import Tuple


class SerialDecoder:
    '''
    逐次入力されるバイトデータからシリアル通信で付加された制御文字を取り除く。
    1サンプル分（1列分のデータ送付フォーマット）
    [DLE=0x10, STX=0x02] => データ開始
    [DLE=0x10, ETX=0x03] => データ終了
    [DLE=0x10, DLE=0x10] => データ0x10（制御文字のDLEと区別する為、データ内の0x10は[0x10, 0x10]と入力することにする。
    [DLE=0x10, N]        => エラー。Nは0x02/0x03/0x10ではない。実装上はデータNが入力されたことにする。,
    '''

    def __init__(self, dle: bytes = b'\x10', stx: bytes = b'x02', etx: bytes = b'0x03') -> None:
        self.dle: bytes = dle
        self.stx: bytes = stx
        self.etx: bytes = etx
        self.data_start: bool = False
        self.had_dle: bool = False

    def decode(self, b: bytes) -> Tuple[bool, None | bytes]:
        '''
        1バイトずつ入力し、制御文字を取り除いたデータを出力する。
        戻り値:
        * bool          制御文字によってデータの入力が開始状態にあるかを返す。（開始状態にない場合、バイトデータは常にNoneが返る。）
        * None|bytes    制御文字を取り除いたバイトデータを出力する。制御文字が入力された場合などはNoneを返す。
        '''
        data: None | bytes = None
        
        if b == self.dle:
            # 前回の入力でDLEが入力されていたか
            if not self.had_dle:
                # DLEが入力されたので次の制御文字を待つ。
                self.had_dle = True
                data = None
            else:
                # [DLE, DLE] => データ0x10(DLE)を受信
                self.had_dle = False
                data = self.dle
        elif b == self.stx:
            # 前回の入力でDLEが入力されていたか
            if self.had_dle:
                # 前回の入力でDLEが入力された為、データ入力の開始を検知
                # 既にデータ入力が開始していた場合でもデータはNoneを返す。
                self.had_dle = False
                self.data_start = True
                data = None
            else:
                # ただのデータ0x02(STX)としてデータとして認識する
                data = self.stx
        elif b == self.etx:
            # 前回の入力でDLEが入力されていたか
            if self.had_dle:
                # 前回の入力でDLEが入力された為、データ入力の終了を検知
                # 既にデータ入力が終了していた場合でもデータはNoneを返す。
                self.had_dle = False
                self.data_start = False
                data = None
            else:
                # ただのデータ0x03(ETX)としてデータを認識する
                data = self.etx
        else:
            # 前回の入力でDLEが入力されていたか
            if self.had_dle:
                # [DLE, otherwise]はプロトコルとしてはエラーだが、実装上はotherwiseをdataとして読み込む
                data = b
            else:
                data = b

        if self.data_start:
            return (True, data)
        else:
            return (False, None)
