import json
import os
from InterfaceParam import InterfaceCard, Device, InputParameter, OutputParameter, InputParameter16bit

# --- 関数マッピング ---
# JSON内の文字列を実際の関数オブジェクトに変換するための辞書
func_map = {
    "fpgaver_handler": fpgaver_handler,
    "rsw_handler": rsw_handler,
    "displaymode_handler": displaymode_handler,
    "ethport1_linkgood_handler": ethport1_linkgood_handler,
    "ethport2_linkgood_handler": ethport2_linkgood_handler,
    "ethport3_linkgood_handler": ethport3_linkgood_handler,
    "backlight1_error_handler": backlight1_error_handler,
    "backlight2_error_handler": backlight2_error_handler,
    "backlight1_duty_handler": backlight1_duty_handler,
    "backlight2_duty_handler": backlight2_duty_handler,
    "choice_12": create_choice_validator([1, 2]),
    "choice_bool": create_choice_validator([0, 1]),
    "validate_hex6": validate_16bit_hex_6culum,
    "validate_percent": validate_percent
}

def main(config_file="config.json"):
    # 1. JSON読み込み
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    mlb = InterfaceCard(card_directory=config["card_directory"])

    # 2. デバイスの構築
    for dev_name, params_info in config["devices"].items():
        params = []
        for p in params_info:
            # func_mapから関数を取得 (なければNone)
            v_func = func_map.get(p.get("v"))
            in_func = func_map.get(p.get("in"))
            out_func = func_map.get(p.get("out"))

            if p["type"] == "in":
                param = InputParameter(p["file"], value=p["val"], validator_func=v_func, input_func=in_func)
            elif p["type"] == "out":
                param = OutputParameter(p["file"], value=p["val"], validator_func=v_func, output_func=out_func)
            params.append(param)
        
        mlb.add_device(Device(directory_name=dev_name, parameters=params))

    # 3. 実行
    print(f"--- 処理開始 (Config: {config_file}) ---")
    mlb.update_status()
    print("--- 処理終了 ---")

if __name__ == "__main__":
    main()
    