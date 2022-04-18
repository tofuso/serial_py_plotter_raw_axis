from enum import Enum


class SerialByteProcessor:

    '''
    serial通信で得られたプロトコルによるバイト列からデータへ変換する。
    '''

    def __init__(self, format_list: list[str]) -> None:
        '''
        format_listは、1サンプルで送られてくるデータ列を指定する。
        例:
        [uint8 float int16 fp16q14]
        受信可能なデータ:
        * uint8/16/32/64: 符号なし整数型 8/16/32/64ビット
        * int8/16/32/64: 符号つき整数型 8/16/32/64ビット
        * float/double: 浮動小数点型 32/64ビット
        * fp{X}q{Y}: 固定小数点型 X=ビット長 Y=小数部 例: fp32q16
        '''


class VariousDataType(Enum):
    '''
    VariousDataクラスのデータ種を指定する。
    '''
    UINT8 = 1
    UINT16 = 2
    UINT32 = 3
    UINT64 = 4
    INT8 = 11
    INT16 = 12
    INT32 = 13
    INT64 = 14
    FLOAT = 21
    DOUBLE = 22
    # 固定小数点型
    FP = 31


class VariousData:
    '''
    SerialByteProcessor型が保持する多種型クラス。
    uint8やfloat型を指定して、バイトを入力することで、値が取り出せる。
    '''

    def __init__(self, type_format: VariousDataType, fp_word: int = 0, fp_fraction: int = 0) -> None:
        '''
        引数
        type_format: 扱う型を指定する。
        fp_word/fp_fraction: type_formatにFP（固定小数点型）が選択された時のデータ長と小数部の長さを指定する。
        '''
        self.type_length = 0
        self.fp_fraction = 0
        self.byte_data = []

        if type_format == VariousDataType.UINT8:
            self.type_format = type_format
            self.type_length = 8

        elif type_format == VariousDataType.UINT16:
            self.type_format = type_format
            self.type_length = 16

        elif type_format == VariousDataType.UINT32:
            self.type_format = type_format
            self.type_length = 32

        elif type_format == VariousDataType.UINT64:
            self.type_format = type_format
            self.type_length = 64

        elif type_format == VariousDataType.INT8:
            self.type_format = type_format
            self.type_length = 8

        elif type_format == VariousDataType.INT16:
            self.type_format = type_format
            self.type_length = 16

        elif type_format == VariousDataType.INT32:
            self.type_format = type_format
            self.type_length = 32

        elif type_format == VariousDataType.INT64:
            self.type_format = type_format
            self.type_length = 64

        elif type_format == VariousDataType.FLOAT:
            self.type_format = type_format
            self.type_length = 32

        elif type_format == VariousDataType.DOUBLE:
            self.type_format = type_format
            self.type_length = 64

        elif type_format == VariousDataType.FP:  # 固定小数点型
            self.type_format = type_format
            self.type_length = fp_word
            self.fp_fraction = fp_fraction

        else:
            raise NameError("VariousData type Error")

    def read_byte(self, b: bytes) -> None | int | float:
        '''
        1バイトの入力を受けてバイトを溜める。
        指定型のデータまで足りない場合はNoneを出力し、データが完成した場合は値が返る。
        整数型が指定されている場合はint型、浮動小数点型、固定小数点型が指定された場合はfloat型が返る。
        '''
        self.byte_data += b
        if len(self.byte_data) >= self.type_length:
            # データが完成、型に変換して戻り値に返す。
            pass
        return None
