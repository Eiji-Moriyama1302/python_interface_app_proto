import json
import os
import time
from InterfaceParam import InterfaceCard, Device, InputParameter, OutputParameter
from mlb_func import func_map
from mlb_ctrl import MlbCtrl

def main(config_file:str="config.json"):
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
    