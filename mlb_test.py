#!/usr/bin/env python3
import time
import os

from mlb_param import InterfaceCard, Device, InputParameter, OutputParameter, InputParameter16bit

def fpgaver_handler():
    print(f"exec fpgaver_handler.")
    return "1234"

def rsw_handler():
    print(f"exec rsw_handler.")
    return "543210"

def displaymode_handler(value):
    print(f"exec displaymode_handler. {value}")

def ethport1_linkgood_handler():
    print(f"exec ethport1_linkgood_handler.")
    return "0"

def ethport2_linkgood_handler():
    print(f"exec ethport2_linkgood_handler.")
    return "0"

def ethport3_linkgood_handler():
    print(f"exec ethport3_linkgood_handler.")
    return "1"

def backlight1_error_handler():
    print(f"exec backlight1_error_handler.")
    return "0"

def backlight2_error_handler():
    print(f"exec backlight2_error_handler.")
    return "1"

def backlight1_duty_handler():
    print(f"exec backlight1_duty_handler.")
    return "20"

def backlight2_duty_handler():
    print(f"exec backlight2_duty_handler.")
    return "40"

# より汎用的に作るなら（引数で選択肢を指定できるクロージャ形式）
def create_choice_validator(choices):
    """指定されたリストのいずれかに含まれるかチェックする関数を返す"""
    def validator(value):
        # 数値と文字列の両方を考慮するため、すべて文字列に変換して比較
        return str(value) in [str(c) for c in choices]
    return validator

def validate_16bit_hex_6culum(val):
    import re

    if val is None:
        return False
    # 文字列に変換
    s_val = str(val).strip()
    # 0x または 0X 始まりを許容する正規表現
    # 1. 0xがある場合、その後に1～6桁の16進数文字
    # 2. 0xがない場合、1～6桁の16進数文字
    pattern = r'^(0[xX])?[0-9a-fA-F]{1,6}$'
    
    if re.match(pattern, s_val):
        try:
            # 数値として0xFFFF以下であることを確認
            return int(s_val, 16) <= 0xFFFFFF
        except ValueError:
            return False
    return False

def validate_percent(val):
    import re

    if val is None:
        return False
    # 文字列に変換
    s_val = str(val).strip()
    # 0x または 0X 始まりを許容する正規表現
    # 1. 0xがある場合、その後に1～6桁の16進数文字
    # 2. 0xがない場合、1～6桁の16進数文字
    pattern = r'^(0[xX])?[0-9a-fA-F]{1,6}$'
    
    if re.match(pattern, s_val):
        try:
            # 数値として100以下であることを確認
            return int(s_val, 16) <= 100
        except ValueError:
            return False
    return False

def main():
    # 1. パラメータのインスタンス化
    fpgaver = InputParameter16bit(
        filename="fpgaver", 
        value="----",
        input_func=fpgaver_handler
    )
    
    choice_12_validator = create_choice_validator([1, 2])
    # Output: ディスプレイモードの設定
    displaymode = OutputParameter(
        filename="display_mode",
        value="1",
        validator_func=choice_12_validator,
        output_func=displaymode_handler
    )

    rsw = InputParameter(
        filename="rsw", 
        value="------",
        validator_func=validate_16bit_hex_6culum,
        input_func=rsw_handler
    )
    
    # 2. Deviceクラスのインスタンス作成
    fpga = Device(
        directory_name="fpga", 
        parameters=[fpgaver, displaymode, rsw]
    )

    choice_bool_validator = create_choice_validator([0, 1])
    linkgood1 = InputParameter(
        filename="linkgood", 
        value="-",
        validator_func=choice_bool_validator,
        input_func=ethport1_linkgood_handler
    )
    
    linkgood2 = InputParameter(
        filename="linkgood", 
        value="-",
        validator_func=choice_bool_validator,
        input_func=ethport2_linkgood_handler
    )
    
    linkgood3 = InputParameter(
        filename="linkgood", 
        value="-",
        validator_func=choice_bool_validator,
        input_func=ethport3_linkgood_handler
    )
    
    ethport1 = Device(
        directory_name="ethport1", 
        parameters=[linkgood1]
    )

    ethport2 = Device(
        directory_name="ethport2", 
        parameters=[linkgood2]
    )

    ethport3 = Device(
        directory_name="ethport3", 
        parameters=[linkgood3]
    )

    backlight1error = InputParameter(
        filename="error", 
        value="-",
        validator_func=choice_bool_validator,
        input_func=backlight1_error_handler
    )
    
    backlight1duty = InputParameter(
        filename="duty", 
        value="-",
        validator_func=validate_percent,
        input_func=backlight1_duty_handler
    )
    
    backlight2error = InputParameter(
        filename="error", 
        value="-",
        validator_func=choice_bool_validator,
        input_func=backlight2_error_handler
    )
    
    backlight2duty = InputParameter(
        filename="duty", 
        value="-",
        validator_func=validate_percent,
        input_func=backlight2_duty_handler
    )
    
    backlight1 = Device(
        directory_name="backlight1", 
        parameters=[backlight1error, backlight1duty]
    )
    
    backlight2 = Device(
        directory_name="backlight2", 
        parameters=[backlight2error, backlight2duty]
    )

    # 3. InterfaceCardクラスのインスタンス作成 (mlb)
    # ルートディレクトリを "mlb_root" とします
    mlb = InterfaceCard(card_directory="/tmp/mlb")

    # 4. mlbにデバイスを追加
    mlb.add_device(fpga)
    mlb.add_device(ethport1)
    mlb.add_device(ethport2)
    mlb.add_device(ethport3)
    mlb.add_device(backlight1)
    mlb.add_device(backlight2)

    displaymode._update_file("2")

    # 5. アクセスメソッドの実行
    # これにより、mlb_root/fpga_subsystem/ 配下のファイルが処理されます
    print("--- 処理開始 ---")
    mlb.update_status()
    print("--- 処理終了 ---")

if __name__ == "__main__":
    # テスト用にディレクトリがない場合は作成するなどの準備が必要ですが、
    # クラス内の validate メソッドがディレクトリ存在チェックを行う仕様になっています。
    main()
