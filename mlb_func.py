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

def backlight_on_handler(self,value):
    print(f"exec backlight_on_handler.")
    if value == "1":
        self.ctrl.backlight_turnon()
    if value == "0":
        self.ctrl.backlight_turnoff()
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


