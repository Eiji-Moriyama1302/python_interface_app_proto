import time
import os
from InterfaceParam import InterfaceCard, Device, InputParameter, OutputParameter, InputParameter16bit

# --- バリデータ定義（クロージャで生成） ---
validate_hex6 = validate_16bit_hex_6culum  # 既存の関数を流用
validate_percent = validate_percent        # 既存
choice_12 = create_choice_validator([1, 2])
choice_bool = create_choice_validator([0, 1])

def main():
    mlb = InterfaceCard(card_directory="/tmp/mlb")

    # 1. デバイスとパラメータの構成定義（ここを編集するだけで追加・変更が可能）
    devices_config = {
        "fpga": [
            {"type": "hex16", "file": "fpgaver", "val": "----", "in": fpgaver_handler},
            {"type": "out",   "file": "display_mode", "val": "1", "v": choice_12, "out": displaymode_handler},
            {"type": "in",    "file": "rsw", "val": "------", "v": validate_hex6, "in": rsw_handler},
        ],
        "ethport1": [{"type": "in", "file": "linkgood", "val": "-", "v": choice_bool, "in": ethport1_linkgood_handler}],
        "ethport2": [{"type": "in", "file": "linkgood", "val": "-", "v": choice_bool, "in": ethport2_linkgood_handler}],
        "ethport3": [{"type": "in", "file": "linkgood", "val": "-", "v": choice_bool, "in": ethport3_linkgood_handler}],
        "backlight1": [
            {"type": "in", "file": "error", "val": "-", "v": choice_bool, "in": backlight1_error_handler},
            {"type": "in", "file": "duty",  "val": "-", "v": validate_percent, "in": backlight1_duty_handler},
        ],
        "backlight2": [
            {"type": "in", "file": "error", "val": "-", "v": choice_bool, "in": backlight2_error_handler},
            {"type": "in", "file": "duty",  "val": "-", "v": validate_percent, "in": backlight2_duty_handler},
        ],
    }

    # 2. 定義データに基づいてインスタンスを一括生成
    for dev_name, params_info in devices_config.items():
        params = []
        for p in params_info:
            if p["type"] == "hex16":
                param = InputParameter16bit(p["file"], value=p["val"], input_func=p.get("in"))
            elif p["type"] == "in":
                param = InputParameter(p["file"], value=p["val"], validator_func=p.get("v"), input_func=p.get("in"))
            elif p["type"] == "out":
                param = OutputParameter(p["file"], value=p["val"], validator_func=p.get("v"), output_func=p.get("out"))
            params.append(param)
        
        mlb.add_device(Device(directory_name=dev_name, parameters=params))

    # 3. 実行
    print("--- 処理開始 ---")
    mlb.update_status()
    print("--- 処理終了 ---")

if __name__ == "__main__":
    main()
    