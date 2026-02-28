import os
import re

from typing import Callable, Any, Optional
from InterfaceCtrl import InterfaceCtrl

class BaseParameter:
    """共通のプロパティを持つベースクラス"""
    def __init__(self, filename:str, value:int=None, validator_func=None, input_func=None, output_func=None):
        self.filename = filename
        self._value = value
        self.full_path = None
        self.validator_func = validator_func
        self.input_func = input_func
        self.output_func = output_func

    def validate(self,value:int) -> bool:
        """共通のバリデーション（例：ファイル名の存在チェック）"""
        if not self.filename:
            print("エラー: ファイル名が空です。")
            return False
        if self.validator_func:
            if not self.validator_func(value):
                print(f"エラー: 独自バリデーションに失敗しました ({self.filename}={value})")
                return False
        return True

    def prepare_file(self, target_dir:str) -> None:
        """ファイルが存在しない場合に作成するメソッド"""
        full_path = os.path.join(target_dir, self.filename)
        if not full_path:
            return
        
        self.full_path = full_path

        if not os.path.exists(self.full_path):
            print(f"prepare path: {self.full_path}")
            # ディレクトリの再確認（ファイル名にパスが含まれる場合用）
            os.makedirs(os.path.dirname(self.full_path), exist_ok=True)
            
            # 初期値があれば書き込み、なければ空ファイル作成
            self._update_file(None, self._value)
            print(f"[Input] ファイルを新規作成しました: {self.full_path}")
        else:
            print(f"already exist path: {self.full_path}")
    
    def _update_file(self, Controller:InterfaceCtrl, value:int) -> None:
        content = str(value) if value is not None else ""
        with open(self.full_path, 'w', encoding='utf-8') as f:
            f.write(str(content))

    def _read_file_content(self, Contoller:InterfaceCtrl) -> str:
        """
        共通メソッド: ファイルの存在を確認し、内容を読み出す
        ファイルが存在しない場合は None を返す
        """
        if not os.path.exists(self.full_path):
            return None
        try:
            with open(self.full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"ファイル読み込みエラー ({self.full_path}): {e}")
            return None
        
    # リファクタリング用補助メソッド（コードの重複を避ける場合）
    def _get_processed_input(self, controller: InterfaceCtrl):
        new_val = self.input_func(controller) if self.input_func else None
        return str(new_val).splitlines()[0] if new_val else new_val

    def _apply_update(self, controller: InterfaceCtrl, value: int):
        self._value = value
        if self.output_func:
            self.output_func(controller, self._value)
        print(f"[Output] パラメータを更新しました（強制）: {self._value}")

    def handle_access(self, controller: InterfaceCtrl) -> None: 
        """
        通常アクセス：値に変化があった場合のみ更新・通知を行う
        """
        processed_value = self._get_processed_input(controller)
        
        if processed_value is None:
            return

        # 既存ロジック：バリデーション OK かつ 値に変化がある場合
        if self.validate(processed_value) and processed_value != self._value:
            self._apply_update(controller, processed_value)

    def handle_access_always(self, controller: InterfaceCtrl) -> None:
        """
        強制アクセス：値の変化に関わらず、バリデーションが通れば更新・通知を実行する
        """
        processed_value = self._get_processed_input(controller)
        
        if processed_value is None:
            return

        # 変更点：値の比較 (processed_value != self._value) を行わない
        if self.validate(processed_value):
            self._apply_update(controller, processed_value)
        

class InputParameter(BaseParameter):
    """入力用パラメータクラス"""
    def __init__(
            self, 
            filename:str, 
            value:int=None, 
            validator_func: Optional[Callable[[Any], bool]]=None, 
            input_func: Optional[Callable] = None
    ):
        output_func = self._update_file
        super().__init__(filename, value, validator_func, input_func, output_func)
        

class OutputParameter(BaseParameter):
    """出力用パラメータクラス（ファイル -> メモリ）"""
    def __init__(
            self, 
            filename:str, 
            value:int=None, 
            validator_func: Optional[Callable[[Any], bool]] = None, 
            output_func: Optional[Callable[[Optional[InterfaceCtrl], Any], Any]] = None
    ):
        input_func = self._read_file_content
        super().__init__(filename, value, validator_func, input_func, output_func)
        

class Device:
    def __init__(self, directory_name:str, parameters:BaseParameter=None):
        """
        :param directory_name: ベースとなるディレクトリ名
        :param parameters: InputParameter または OutputParameter のリスト
        """
        self.directory_name = directory_name
        self.parameters = parameters if parameters is not None else []

    def access(self,controlller:InterfaceCtrl) -> None:
        """
        全パラメータに対して、仕様に基づいたアクセスメソッドを実行する
        """
        for param in self.parameters:
            param.handle_access(controlller)

class InterfaceCard:
    """
    複数のInterfaceを束ねて管理するカードクラス
    """
    def __init__(self, InterfaceCtrl:InterfaceCtrl, card_directory:str, Devices:Device=None):
        """
        :param card_directory: カードのルートディレクトリ名
        :param devices: device
        """
        self.card_directory = card_directory
        self.ctrl = InterfaceCtrl()
        self.ctrl.open()
        self.ctrl.refresh()
        self.ctrl.close()
        self.devices = []
        if Devices:
            for device in Devices:
                self.add_device(device)

    def update_status(self) -> None:
        """
        保持している全てのInterfaceのアクセスメソッドを順次実行する
        """
        print(f"--- Card Status update Start: {self.card_directory} ---")

        self.ctrl.open()
        
        self.ctrl.refresh()
        
        for device in self.devices:
            # 各deviceのアクセス処理を実行
            device.access(self.ctrl)
            
        self.ctrl.close()

        print(f"--- Card status update End ---")

    def add_device(self, device:Device) -> None:
        """deviceを動的に追加するメソッド"""
        print(f"--- Card add_device Start: {device.directory_name} ---")
        self.devices.append(device)

        # 1. インターフェース用のディレクトリを作成
        target_dir = os.path.join(self.card_directory, device.directory_name)
        print(f"makedirs: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        
        self.ctrl.open()
        
        # 2. 配下の全パラメータに対してパス設定とファイル作成を行う
        for param in device.parameters:
            # ファイルの物理作成
            param.prepare_file(target_dir)
            param.handle_access_always(self.ctrl)
        
        self.ctrl.close()

        print(f"--- Card add_device End: {device.directory_name} ---")
