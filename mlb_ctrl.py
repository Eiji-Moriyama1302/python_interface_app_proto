from typing import Optional, Tuple
from InterfaceCtrl import InterfaceCtrl

class MlbCtrl(InterfaceCtrl):
    def __init__(self):
        super().__init__()
        print("MlbCtrl instance created\n")
    
    def open(self) -> None:
        print("MlbCtrl: MLB API への接続を開始します...")
    
    def refresh(self) -> None:
        print("MlbCtrl: リーグの最新スコアを取得中...")

    def close(self) -> None:
        print("MlbCtrl: セッションを正常に終了しました。")

    def get_fpgaver(self) -> Optional[str]:
        print(f"exec get_fpgaver.")
        return "2512"

    def get_id(self) -> Optional[str]:
        return "17"

    def get_rsw(self) -> Optional[str]:
        return "543211"

    def get_ether_statuses(self, port_num: int) -> Optional[Tuple[str, str]]:
        return f"{port_num:04X}"

    def get_backlight_statuses(self) -> Optional[Tuple[str, str]]:
        return "0123"

    def get_backlight_pwm_duty(self, port_num: int) -> Optional[Tuple[str, str]]:
        return "0020"

    def backlight_turnon(self) -> None:
        print("MlbCtrl: backlight_turnon")

    def backlight_turnoff(self) -> None:
        print("MlbCtrl: backlight_turnoff")
    
    def set_brightness(self, value: int) -> bool:
        return True
    
    def display_mode_single(self) -> None:
        print("MlbCtrl: single display mode")
    
    def display_mode_double(self) -> None:
        print("MlbCtrl: double display mode")

    def set_testled(self, enable: bool) -> None:
        if enable == True:
            print("MlbCtrl: testled turnon")
        else:
            print("MlbCtrl: testled turnoff")
