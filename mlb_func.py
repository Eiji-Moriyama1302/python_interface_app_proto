from typing import Iterable, Any, Callable
from mlb_ctrl import MlbCtrl

def fpgaver_handler(controller:MlbCtrl) -> str:
    return controller.get_fpgaver()

def rsw_handler(controller:MlbCtrl) -> str:
    return controller.get_rsw()

def displaymode_handler(controller:MlbCtrl,value:str) -> None:
    if value == "1":
        controller.display_mode_single()
    if value == "2":
        controller.display_mode_double()

def ethport1_linkgood_handler(controller:MlbCtrl) -> str:
    return controller.get_ether_statuses(1)

def ethport2_linkgood_handler(controller:MlbCtrl) -> str:
    return controller.get_ether_statuses(2)

def ethport3_linkgood_handler(controller:MlbCtrl) -> str:
    return controller.get_ether_statuses(3)

def backlight1_error_handler(controller:MlbCtrl) -> str:
    print(f"exec backlight1_error_handler.")
    return "0"

def backlight2_error_handler(controller:MlbCtrl) -> str:
    print(f"exec backlight2_error_handler.")
    return "1"

def backlight1_duty_handler(controller:MlbCtrl) -> str:
    return controller.get_backlight_pwm_duty(1)

def backlight2_duty_handler(controller:MlbCtrl) -> str:
    return controller.get_backlight_pwm_duty(2)

def backlight1_on_handler(controller:MlbCtrl,value: str) -> str:
    if value == "1":
        controller.backlight1_turnon()
    if value == "0":
        controller.backlight1_turnoff()
    return "40"

def backlight2_on_handler(controller:MlbCtrl,value: str) -> str:
    if value == "1":
        controller.backlight2_turnon()
    if value == "0":
        controller.backlight2_turnoff()
    return "40"

# より汎用的に作るなら（引数で選択肢を指定できるクロージャ形式）
def create_choice_validator(choices:Iterable[Any]) -> Callable[[Any], bool]:
    """指定されたリストのいずれかに含まれるかチェックする関数を返す"""
    def validator(value):
        # 数値と文字列の両方を考慮するため、すべて文字列に変換して比較
        return str(value) in [str(c) for c in choices]
    return validator

def validate_16bit_hex_6culum(val:int) -> bool:
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

def validate_percent(val:int) -> bool:
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
    "backlight1_on_handler": backlight1_on_handler,
    "choice_12": create_choice_validator([1, 2]),
    "choice_bool": create_choice_validator([0, 1]),
    "validate_hex6": validate_16bit_hex_6culum,
    "validate_percent": validate_percent
}
