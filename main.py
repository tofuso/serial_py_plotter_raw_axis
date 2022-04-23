# プログラムのエントリポイント
# コマンドによって各モジュールを制御する。
from typing import Tuple
from .serial import serial_reader
from .serial_processor import serial_decoder

mode: str = "bin"
serial_port: str = "COM3"
serial_baudrate: int = 115200

if __name__ == "__main__":
    serial = serial_reader.SerialReader(serial_port, serial_baudrate, 1.0)
    protocol_decode = serial_decoder.SerialDecoder()

    while True:
        # シリアル通信でデータを読み込み
        b: bytes = serial.read_byte()
        # rawデータの通信開始制御をデコード
        raw_data: Tuple[bool, None | bytes] = protocol_decode.decode(b)
        if raw_data[1] == None:
            continue
        else:
            b = raw_data[1]
        
