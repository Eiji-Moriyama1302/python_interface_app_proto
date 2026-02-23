import unittest
from unittest.mock import patch
import io
import sys
from abc import ABC

# テスト対象のクラスをインポート（ファイル名に合わせて変更してください）
from InterfaceCtrl import InterfaceCtrl

class TestInterfaceCtrl(unittest.TestCase):
    def setUp(self):
        """
        抽象クラスをテストするために、一時的な具象クラスを作成します。
        """
        class ConcreteInterfaceCtrl(InterfaceCtrl):
            def open(self) -> None:
                print("Open called")
                
            def refresh(self) -> None:
                print("Refresh called")
                
            def close(self) -> None:
                print("Close called")
        
        self.concrete_class = ConcreteInterfaceCtrl

    def test_cannot_instantiate_abstract_class(self):
        """抽象クラス自体をインスタンス化しようとすると TypeError が発生することを確認"""
        with self.assertRaises(TypeError):
            InterfaceCtrl()

    def test_init_print_output(self):
        """__init__ 時に指定の文字列が標準出力に表示されるかを確認"""
        # 標準出力をキャプチャするための準備
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # 具象クラスのインスタンス化（親の __init__ が呼ばれる）
            self.concrete_class()
            
            # 出力の検証
            output = captured_output.getvalue()
            self.assertIn("Call InterfaceCtrl::__init__", output)
        finally:
            # 標準出力を元に戻す
            sys.stdout = sys.__stdout__

    def test_concrete_methods(self):
        """具象クラスが全ての抽象メソッドを正しく実装できているかを確認"""
        ctrl = self.concrete_class()
        
        # 各メソッドがエラーなく実行できること
        try:
            ctrl.open()
            ctrl.refresh()
            ctrl.close()
        except TypeError as e:
            self.fail(f"Abstract method implementation failed: {e}")

if __name__ == '__main__':
    unittest.main()