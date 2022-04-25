from enum import Enum
import re
import struct
import sys


class VariousDataEndian(Enum):
    BIGENDIAN = 0
    LITTLEENDIAN = 1


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

    def __init__(self, type_format: VariousDataType, endian: VariousDataEndian, fp_word: int = 0, fp_fraction: int = 0) -> None:
        '''
        引数
        type_format: 扱う型を指定する。
        fp_word/fp_fraction: type_formatにFP（固定小数点型）が選択された時のデータ長と小数部の長さを指定する。
        '''
        self.bytes_length = 0
        self.fp_fraction = 0
        self.endian = endian
        self.is_empty_bytes: bool = True
        self.bytes_data: bytes = b"\x00"

        if type_format == VariousDataType.UINT8:
            self.type_format = type_format
            self.bytes_length = 1

        elif type_format == VariousDataType.UINT16:
            self.type_format = type_format
            self.bytes_length = 2

        elif type_format == VariousDataType.UINT32:
            self.type_format = type_format
            self.bytes_length = 4

        elif type_format == VariousDataType.UINT64:
            self.type_format = type_format
            self.bytes_length = 8

        elif type_format == VariousDataType.INT8:
            self.type_format = type_format
            self.bytes_length = 1

        elif type_format == VariousDataType.INT16:
            self.type_format = type_format
            self.bytes_length = 2

        elif type_format == VariousDataType.INT32:
            self.type_format = type_format
            self.bytes_length = 4

        elif type_format == VariousDataType.INT64:
            self.type_format = type_format
            self.bytes_length = 8

        elif type_format == VariousDataType.FLOAT:
            self.type_format = type_format
            self.bytes_length = 4

        elif type_format == VariousDataType.DOUBLE:
            self.type_format = type_format
            self.bytes_length = 8

        elif type_format == VariousDataType.FP:  # 固定小数点型
            self.type_format = type_format
            self.bytes_length = fp_word
            self.fp_fraction = fp_fraction

        else:
            raise NameError("VariousData type Error")

    def clear_byte(self):
        '''
        溜め込んでいるバイトデータをクリアする。
        '''
        self.is_empty_bytes = True

    def read_byte(self, b: bytes) -> None | int | float:
        '''
        1バイトの入力を受けてバイトを溜める。
        指定型のデータまで足りない場合はNoneを出力し、データが完成した場合は値が返る。
        整数型が指定されている場合はint型、浮動小数点型、固定小数点型が指定された場合はfloat型が返る。
        '''
        if self.is_empty_bytes:
            self.is_empty_bytes = False
            self.bytes_data = b
        else:
            self.bytes_data += b
        if len(self.bytes_data) >= self.bytes_length:
            # データが完成、指定された型に変換して戻り値に返す。
            if self.type_format == VariousDataType.UINT8 or \
                    self.type_format == VariousDataType.UINT16 or \
                    self.type_format == VariousDataType.UINT32 or \
                    self.type_format == VariousDataType.UINT64:

                if self.endian == VariousDataEndian.BIGENDIAN:
                    self.is_empty_bytes = True
                    return int.from_bytes(self.bytes_data, byteorder='big', signed=False)
                else:
                    self.is_empty_bytes = True
                    return int.from_bytes(self.bytes_data, byteorder='little', signed=False)

            elif self.type_format == VariousDataType.INT8 or \
                    self.type_format == VariousDataType.INT16 or \
                    self.type_format == VariousDataType.INT32 or \
                    self.type_format == VariousDataType.INT64:

                if self.endian == VariousDataEndian.BIGENDIAN:
                    self.is_empty_bytes = True
                    return int.from_bytes(self.bytes_data, byteorder='big', signed=True)
                else:
                    self.is_empty_bytes = True
                    return int.from_bytes(self.bytes_data, byteorder='little', signed=True)

            elif self.type_format == VariousDataType.FLOAT:

                if self.endian == VariousDataEndian.BIGENDIAN:
                    self.is_empty_bytes = True
                    return struct.unpack(">f", self.bytes_data)[0]
                else:
                    self.is_empty_bytes = True
                    return struct.unpack("<f", self.bytes_data)[0]

            elif self.type_format == VariousDataType.DOUBLE:

                if self.endian == VariousDataEndian.BIGENDIAN:
                    self.is_empty_bytes = True
                    return struct.unpack(">d", self.bytes_data)[0]
                else:
                    self.is_empty_bytes = True
                    return struct.unpack("<d", self.bytes_data)[0]
            else:
                # TODO: 固定小数点 → float型に変換する処理を書く
                pass
        return None


class SerialByte2Data:

    '''
    serial通信で得られたプロトコルによるバイト列からデータへ変換する。
    '''

    def __init__(self, data_format_list: list[str], endian: VariousDataEndian) -> None:
        '''
        format_listは、1サンプルで送られてくるデータ列を指定する。
        例:
        ["uint8", "float", "int16", "fp16q14"]
        受信可能なデータ:
        * uint8/16/32/64: 符号なし整数型 8/16/32/64ビット
        * int8/16/32/64: 符号つき整数型 8/16/32/64ビット
        * float/double: 浮動小数点型 32/64ビット
        * fp{X}q{Y}: 固定小数点型 X=ビット長 Y=小数部 例: fp32q16
        '''
        # 1サンプル毎に送られてくるデータ列を保持するVariousData配列
        self.data_array: list[VariousData] = []
        # 現在変換を行っているデータのインデックス
        self.i_current_data: int = 0

        for f in data_format_list:
            if f == "uint8":
                self.data_array.append(VariousData(
                    VariousDataType.UINT8, endian))
            elif f == "uint16":
                self.data_array.append(VariousData(
                    VariousDataType.UINT16, endian))
            elif f == "uint32":
                self.data_array.append(VariousData(
                    VariousDataType.UINT32, endian))
            elif f == "uint64":
                self.data_array.append(VariousData(
                    VariousDataType.UINT64, endian))
            elif f == "int8":
                self.data_array.append(VariousData(
                    VariousDataType.INT8, endian))
            elif f == "int16":
                self.data_array.append(VariousData(
                    VariousDataType.INT16, endian))
            elif f == "int32":
                self.data_array.append(VariousData(
                    VariousDataType.INT32, endian))
            elif f == "int64":
                self.data_array.append(VariousData(
                    VariousDataType.INT64, endian))
            elif f == "float":
                self.data_array.append(VariousData(
                    VariousDataType.FLOAT, endian))
            elif f == "double":
                self.data_array.append(VariousData(
                    VariousDataType.DOUBLE, endian))
            else:
                # 固定小数点か正規表現を用いて判定する
                fp_t = re.fullmatch(r"(?i)FP(\d+)Q(\d+)", f)

                if fp_t == None:
                    # 正規表現が一致しない。
                    # 指定された形式以外の型を指定した。
                    print("Incorrect type format. type:{}".format(f),
                          file=sys.stderr)
                    sys.exit(1)

                fp_word: int = int(fp_t.groups()[0])
                fp_fraction: int = int(fp_t.groups()[1])

                if fp_word < fp_fraction:
                    # 固定小数点長よりも小数部の方が長い場合
                    print("The length of the fractional part of the fixe-point is longer than the fixed-point length.",
                          file=sys.stderr)
                    sys.exit(1)

                self.data_array.append(
                    VariousData(VariousDataType.FP, endian, fp_word=fp_word, fp_fraction=fp_fraction))

    def reset_translate(self):
        '''
        溜め込んだバイトをクリアして、変換状態をリセットする。
        '''
        self.i_current_data = 0
        for vd in self.data_array:
            vd.clear_byte()

    def byte2data(self, input_byte: bytes) -> None | int | float:
        '''
        バイトデータの入力を受け、変換を実施する。
        '''
        result = self.data_array[self.i_current_data].read_byte(input_byte)
        if result == None:  # 変換中でデータが出力されない場合はNoneを返す。
            return None
        # 変換が実施され、データが出力された場合は、変換対象に次のデータを指定し、変換されたデータを返す。
        self.i_current_data += 1
        if self.i_current_data >= len(self.data_array):
            # self.i_current_data = 0
            return None
        return result
