import os

class BaseParameter:
    """共通のプロパティを持つベースクラス"""
    def __init__(self, filename, value=None):
        self.filename = filename
        self._value = value

    def validate(self):
        """共通のバリデーション（例：ファイル名の存在チェック）"""
        if not self.filename:
            print("エラー: ファイル名が空です。")
            return False
        return True


class InputParameter(BaseParameter):
    """入力用パラメータクラス"""
    
    def validate(self):
        """有効値チェック：ファイルが存在するか、値が空でないか"""
        if not super().validate():
            return False
        if not os.path.exists(self.filename):
            print(f"エラー: 入力ファイル '{self.filename}' が見つかりません。")
            return False
        if self._value is None:
            print("エラー: 入力値が設定されていません。")
            return False
        print(f"入力チェックOK: {self.filename}")
        return True

    def get_value(self):
        """値取得メソッド"""
        return self._value


class OutputParameter(BaseParameter):
    """出力用パラメータクラス"""

    def validate(self):
        """有効値チェック：出力先ディレクトリが存在するか"""
        if not super().validate():
            return False
        # ディレクトリの存在確認
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            print(f"エラー: 出力先ディレクトリ '{directory}' が存在しません。")
            return False
        print(f"出力チェックOK: {self.filename}")
        return True

    def set_value(self, new_value):
        """値設定メソッド"""
        self._value = new_value
        print(f"値を設定しました: {self._value}")

import os

class Interface:
    def __init__(self, directory_name, parameters=None):
        """
        :param directory_name: ベースとなるディレクトリ名
        :param parameters: InputParameter または OutputParameter のリスト
        """
        self.directory_name = directory_name
        self.parameters = parameters if parameters is not None else []

    def access(self):
        """
        全パラメータに対して、仕様に基づいたアクセスメソッドを実行する
        """
        for param in self.parameters:
            # フルパスの生成
            full_path = os.path.join(self.directory_name, param.filename)
            
            if isinstance(param, InputParameter):
                self._handle_input(param, full_path)
            elif isinstance(param, OutputParameter):
                self._handle_output(param, full_path)

    def _handle_input(self, param, full_path):
        """InputParameter用の処理: get_value -> validate -> 書き込み"""
        current_val = param.get_value()
        
        # バリデーションチェック
        if param.validate():
            # ここでは「値の変化」を記録するために、前回の状態を比較するロジックを想定
            # ファイルの内容と比較して変化があれば書き込む
            if self._has_changed(full_path, current_val):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(str(current_val))
                print(f"[Input] ファイルを更新しました: {full_path}")

    def _handle_output(self, param, full_path):
        """OutputParameter用の処理: ファイル読み込み -> validate -> set_value"""
        if not os.path.exists(full_path):
            return

        with open(full_path, 'r', encoding='utf-8') as f:
            new_val = f.read()

        # 取得した値を一時的にセットしてチェック（あるいは検証用メソッドを呼ぶ）
        # 仕様に基づき、有効かつ変化がある場合に更新
        if param.validate() and new_val != param._value:
            param.set_value(new_val)
            print(f"[Output] パラメータを更新しました: {full_path}")

    def _has_changed(self, path, new_val):
        """ファイルの中身と新しい値に変化があるか確認"""
        if not os.path.exists(path):
            return True
        with open(path, 'r', encoding='utf-8') as f:
            return f.read() != str(new_val)
        