import json
import os
import time
from InterfaceParam import InterfaceCard, Device, InputParameter, OutputParameter
from mlb_func import fpgaver_handler, rsw_handler, displaymode_handler, ethport1_linkgood_handler, ethport2_linkgood_handler, ethport3_linkgood_handler, backlight1_error_handler, backlight2_error_handler, backlight1_duty_handler, backlight2_duty_handler, create_choice_validator, create_choice_validator, validate_16bit_hex_6culum, validate_percent
from mlb_ctrl import MlbCtrl

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

    mlb = InterfaceCard(InterfaceCtrl=MlbCtrl, card_directory=config["card_directory"])

    # 2. デバイスの構築
    for dev_name, params_info in config["devices"].items():
        params = []
        for p in params_info:
            # func_mapから関数を取得 (なければNone)
            v_func = func_map.get(p.get("v"))
            in_func = func_map.get(p.get("in"))
            out_func = func_map.get(p.get("out"))

            param = None
            if p["type"] == "in":
                param = InputParameter(p["file"], value=p["val"], validator_func=v_func, input_func=in_func)
            elif p["type"] == "out":
                param = OutputParameter(p["file"], value=p["val"], validator_func=v_func, output_func=out_func)
            
            if param:
                params.append(param)
        
        mlb.add_device(Device(directory_name=dev_name, parameters=params))

    # 3. 実行
    print(f"--- 監視開始 (1秒周期 / Config: {config_file}) ---")
    print("終了するには Ctrl+C を押してください")
    
    try:
        while True:
            # 状態の更新を実行
            mlb.update_status()
            
            # 次の実行まで1秒待機
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Ctrl+C が押されたときに綺麗に終了する
        print("\n--- 監視を停止しました ---")

if __name__ == "__main__":
    main()
    