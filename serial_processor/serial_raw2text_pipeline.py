from typing import Tuple
from serial_processor.serial_byte2data import VariousDataEndian, SerialByte2Data
from serial_processor.serial_decoder import SerialDecoder, SerialDecoderState


class SerialRaw2TextPipeline:
    '''
    シリアル通信によって逐次入力されるバイトの生データを、テキスト形式に変換する。

    以下の処理を行う。

    * [Serial入力] -(bytes)-> [制御コード処理] -(bytes|None)-> [データに変換] -(data) -> [データをテキスト整形して出力]
    '''

    def __init__(self, data_format_list: list[str],
                 dle: bytes = b"\x10", stx: bytes = b"\x02", etx: bytes = b"\x03",
                 delimiter: str = ",", endian: VariousDataEndian = VariousDataEndian.BIGENDIAN) -> None:
        '''
        送られてくるデータの定義、制御コードの定義を行う。

        引数:

        * data_format_list 入力するデータの型を文字列配列で指定する。
        * dle/stx/etx 制御文字を指定する。
        * delimiter テキストで出力される区切り文字を指定する。
        * endian ビッグエンディアンかリトルエンディアンかを指定する。（デフォルトはmicroblazeに倣いビッグエンディアン。 参考: http://www.kumikomi.net/archives/2008/04/07hard1.php ）
        '''
        self.delimiter = delimiter
        # シリアル通信に含まれる制御文字を変換する。
        self.protocol_decoder = SerialDecoder(dle=dle, stx=stx, etx=etx)
        # バイト列をPythonの内部データに変換する。
        self.byte2data = SerialByte2Data(data_format_list, endian)
        self.output_data_count: int = 0

    def read_byte(self, input_byte: bytes) -> str | None:
        '''
        シリアル通信から読み取った生データの入力を受け、整形済みのテキストを出力する。
        '''
        # バイトデータの通信開始制御をデコード
        decode_result: Tuple[SerialDecoderState,
                             None | bytes] = self.protocol_decoder.decode(input_byte)
        byte_data: bytes

        # データ受信の開始、終了を検知
        current_decoder_state = decode_result[0]
        if current_decoder_state == SerialDecoderState.START:
            # 開始を検知
            self.output_data_count = 0
            self.byte2data.reset_translate()

            # 出力バイトはNoneに固定
            return None

        elif current_decoder_state == SerialDecoderState.FINISH:
            # 終了を検知
            # 出力バイトはNoneに固定されている。
            # サンプルの区切り目のため、改行を出力する。
            self.output_data_count = 0
            self.byte2data.reset_translate()
            return "\n"

        if decode_result[1] == None:
            return None
        else:
            byte_data = decode_result[1]

        # バイトデータをPythonの内部データに変換
        data = self.byte2data.byte2data(byte_data)
        if data == None:
            return None
        else:
            # サンプル内で最初のデータの場合、前に区切り文字は出力しない。
            if self.output_data_count == 0:
                self.output_data_count += 1
                return str(data)
            else:
                self.output_data_count += 1
                return self.delimiter + " " + str(data)
