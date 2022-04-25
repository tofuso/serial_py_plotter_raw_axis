# プログラムのエントリポイント
# コマンドによって各モジュールを制御する。

from serial_processor.serial_byte2data import VariousDataEndian
from serial_processor.serial_raw2text_pipeline import SerialRaw2TextPipeline
from serial_reader.serial_reader import SerialReader
import matplotlib.pyplot as plt


mode: str = "bin"
serial_port: str = "COM3"
serial_baudrate: int = 115200
byte_order = VariousDataEndian.LITTLEENDIAN
data_format = ["float", "float", "float", "float"]
delimiter: str = ","
t: str | None = ""

if __name__ == "__main__":
    serial_reader = SerialReader(serial_port, serial_baudrate, 1.0)
    raw2text = SerialRaw2TextPipeline(data_format, endian=byte_order)

    # プロット用変数
    fig, ax = plt.subplots(1, 1)
    data_count: int = 0
    col_count: int = len(data_format)
    xline: list[int] = [0]
    line_array: list[plt.Line2D] = []
    view_length: int = 100
    data_array: list[list[float]] = [
        [0 for j in range(0, view_length)] for i in range(0, col_count)]

    while True:
        data_line: str = ""

        # データを受信
        if mode == "bin":
            # バイトデータ送信モードは改行が現れるまで処理する
            while True:
                # シリアル通信でデータを読み込み
                b: bytes = serial_reader.read_byte()
                # t: str | None = raw2text.read_byte(b)
                t = raw2text.read_byte(b)

                if t == None:
                    continue

                if t == "\n":
                    break
                data_line += t

        else:
            pass

        # 表示
        # print(data_line, end="")
        # 区切り文字によるデータをパース
        data_count += 1
        for i in range(0, col_count):
            data_line_list: list[str] = [x.strip() for x in data_line.split(delimiter)]
            if i < len(data_line_list):
                try:
                    d_num = float(data_line_list[i])
                except ValueError:
                    print(data_line, "->", data_line_list[i])
                    d_num = 0
            else:
                d_num = 0
            data_array[i].append(d_num)
            del data_array[i][0]

        # プロット
        for i in range(1, col_count):
            if i < len(line_array):
                line_array[i].set_data(
                    data_array[0], data_array[i])
            else:
                lines = ax.plot(data_array[0], data_array[i])
                line_array.append(lines[0])
        xlim_start = data_array[0][-view_length]
        xlim_end = data_array[0][-1]
        ylim_min = min([min(col) for col in data_array[1:]]) * 2
        ylim_max = max([max(col) for col in data_array[1:]]) * 2
        ax.set_xlim([xlim_start, xlim_end])
        ax.set_ylim([ylim_min, ylim_max])
        plt.pause(0.00001)
