import serial


class SerialReader:
    '''
    Serial通信を行いデータを取得する
    '''

    def __init__(self, port: str, baudrate: int, timeout: float | None) -> None:
        self.serial = serial.Serial(
            port=port, baudrate=baudrate, timeout=None)

    def read_byte(self) -> bytes:
        return self.serial.read()

    def close(self):
        self.serial.close()
