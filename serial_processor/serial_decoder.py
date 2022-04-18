class SerialDecoder:
    '''
    逐次入力されるバイトデータからシリアル通信で付加された制御文字を取り除く。
    1サンプル分（1列分のデータ送付フォーマット）
    [DLE=0x10, STX=0x02] => データ開始
    [DLE=0x10, ETX=0x03] => データ終了
    [DLE=0x10, DLE=0x10] => データ0x10（制御文字のDLEと区別する為、データ内の0x10は[0x10, 0x10]と入力することにする。
    [DLE=0x10, N]        => エラー。Nは0x02/0x03/0x10ではない。実装上はデータNが入力されたことにする。,
    '''
    def __init__(self) -> None:
        pass