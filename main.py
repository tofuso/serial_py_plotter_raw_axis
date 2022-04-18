# プログラムのエントリポイント
# コマンドによって各モジュールを制御する。
from .serial import serial_reader

mode: str = "bin"
serial_port: str = "COM3"
serial_baudrate: int = 115200

if __name__ == "__main__":
    serial = serial_reader.SerialReader(serial_port, serial_baudrate, 1.0)

    while True:
        b: bytes = serial.read_byte()
