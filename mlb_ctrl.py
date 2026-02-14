from InterfaceCtrl import InterfaceCtrl

class MlbCtrl(InterfaceCtrl):
    def __init__(self):
        super().__init__()
        print("MlbCtrl instance created\n")
    
    def open(self):
        print("MlbCtrl: MLB API への接続を開始します...")
    
    def refresh(self):
        print("MlbCtrl: リーグの最新スコアを取得中...")

    def close(self):
        print("MlbCtrl: セッションを正常に終了しました。")

    def backlight_turnon(self):
        print("MlbCtrl: backlight_turnon")

    def backlight_turnoff(self):
        print("MlbCtrl: backlight_turnoff")