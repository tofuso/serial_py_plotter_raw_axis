from enum import Enum
from typing import Tuple


class SerialDecoderState(Enum):
    '''
    シリアル通信の制御文字から通信状態の変遷を検知
    '''
    START = 1
    RUNNING = 2
    FINISH = 3
    STOP = 4


class SerialDecoder:
    '''
    逐次入力されるバイトデータからシリアル通信で付加された制御文字を取り除く。

    1サンプル分（1列分のデータ送付フォーマット）
    * [DLE=0x10, STX=0x02] => データ開始
    * [DLE=0x10, ETX=0x03] => データ終了
    * [DLE=0x10, DLE=0x10] => データ0x10（制御文字のDLEと区別する為、データ内の0x10は[0x10, 0x10]と入力することにする。
    * [DLE=0x10, N]        => エラー。Nは0x02/0x03/0x10ではない。実装上はデータNが入力されたことにする。,
    '''

    def __init__(self, dle: bytes = b'\x10', stx: bytes = b'\x02', etx: bytes = b'\x03') -> None:
        self.dle: bytes = dle
        self.stx: bytes = stx
        self.etx: bytes = etx
        self.state: SerialDecoderState = SerialDecoderState.STOP
        self.had_dle: bool = False

    def decode(self, b: bytes) -> Tuple[SerialDecoderState, None | bytes]:
        '''
        1バイトずつ入力し、制御文字を取り除いたデータを出力する。
        戻り値:
        * bool          制御文字によってデータの入力が開始状態にあるかを返す。（開始状態にない場合、バイトデータは常にNoneが返る。）
        * None|bytes    制御文字を取り除いたバイトデータを出力する。制御文字が入力された場合などはNoneを返す。
        '''
        data: None | bytes = None

        # 前回のステートに合わせてステートを更新
        if self.state == SerialDecoderState.START:
            # 前回、STARTステートだった場合、制御文字が入力されなければ、RUNNINGステートに移行する
            self.state = SerialDecoderState.RUNNING
        elif self.state == SerialDecoderState.FINISH:
            # 前回、FINISHステートだった場合、制御文字が入力されなければ、STOPステートに移行する
            self.state = SerialDecoderState.STOP

        if b == self.dle:
            # 前回の入力でDLEが入力されていたか
            if not self.had_dle:
                # DLEが初めて入力されたので次の制御文字を待つ。
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
                self.state = SerialDecoderState.START
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
                self.state = SerialDecoderState.FINISH
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

        # 動作停止ステート中はデータを処理しない
        if self.state == SerialDecoderState.FINISH or \
                self.state == SerialDecoderState.STOP:
            return (self.state, None)

        return (self.state, data)
