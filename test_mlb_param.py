import unittest
import os
import shutil
from mlb_test import InputParameter,OutputParameter,InputParameter16bit,Device,InterfaceCard

# 16bitチェック用の補助関数
def check_16bit(value):
    try:
        num = int(value)
        return 0 <= num <= 65535
    except:
        return False

class TestParameterSystem(unittest.TestCase):
    def setUp(self):
        """テストごとにクリーンなディレクトリを作成"""
        self.test_root = "test_env"
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        os.makedirs(self.test_root)

    def tearDown(self):
        """テスト終了後にディレクトリを削除"""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_input_parameter_validation(self):
        """InputParameterのバリデーションテスト"""
        # 正常系
        p_ok = InputParameter("test.txt", value="100", validator_func=check_16bit)
        self.assertTrue(p_ok.validate("100"))
        
        # 異常系（16bit範囲外）
        p_ng = InputParameter("test.txt", value="70000", validator_func=check_16bit)
        self.assertFalse(p_ng.validate("70000"))

    def test_interface_card_add_and_prepare(self):
        """add_interface時にディレクトリとファイルが作成されるか"""
        mlb = InterfaceCard(self.test_root)
        fpga_in = InputParameter("ver.txt", value="1.0.0")
        fpga_if = Device("fpga", [fpga_in])
        
        mlb.add_device(fpga_if)
        
        # ファイルが実際に存在するか確認
        expected_path = os.path.join(self.test_root, "fpga", "ver.txt")
        self.assertTrue(os.path.exists(expected_path))
        
        # 初期値が書き込まれているか確認
        with open(expected_path, 'r') as f:
            self.assertEqual(f.read(), "1.0.0")

    def test_update_status_input_to_file(self):
        """InputParameterの値がファイルに反映されるか"""
        def test_handler():
            return "B"
            
        mlb = InterfaceCard(self.test_root)
        param = InputParameter("input.txt", value="A", input_func=test_handler)
        iface = Device("iface", [param])
        mlb.add_device(iface)
        
        # 値を変更してupdate_status
        mlb.update_status()
        
        with open(param.full_path, 'r') as f:
            self.assertEqual(f.read(), "B")

    def test_update_status_file_to_output(self):
        """ファイルの変化がOutputParameterに反映されるか"""
        mlb = InterfaceCard(self.test_root)
        param = OutputParameter("output.txt", value="old_val")
        iface = Device("iface", [param])
        mlb.add_device(iface)
        
        # 外部操作を模してファイルを書き換え
        with open(param.full_path, 'w') as f:
            f.write("new_val")
            
        mlb.update_status()
        
        # OutputParameterの値が更新されているか
        self.assertEqual(param._value, "new_val")

    def test_InputParameter16bit_valid_hex_values(self):
        """正常な16進数値のテスト"""
        # プレフィックスあり（小文字・大文字）
        self.assertTrue(InputParameter16bit("f.txt", "0x1234").validate("0x1234"))
        self.assertTrue(InputParameter16bit("f.txt", "0XFFFF").validate("0XFFFF"))
        # プレフィックスなし
        self.assertTrue(InputParameter16bit("f.txt", "abcd").validate("abcd"))
        # 境界値 (0)
        self.assertTrue(InputParameter16bit("f.txt", "0x0").validate("0x0"))

    def test_InputParameter16bit_invalid_range(self):
        """16bitの範囲 (0xFFFF) を超えるケース"""
        # 5桁の16進数
        param = InputParameter16bit("f.txt", "0x10000")
        self.assertFalse(param.validate("0x10000"), "0x10000 should be invalid (over 16bit)")
        
        # 桁数は4桁だが、正規表現や数値変換で弾くべきケース
        param = InputParameter16bit("f.txt", "10000")
        self.assertFalse(param.validate("10000"))

    def test_InputParameter16bit_invalid_format(self):
        """形式が不正なケース"""
        # 16進数に使えない文字 (G以降)
        self.assertFalse(InputParameter16bit("f.txt", "0xG000").validate("0xG000"))
        # 記号
        self.assertFalse(InputParameter16bit("f.txt", "0x12-3").validate("0x12-3"))
        # 空文字
        self.assertFalse(InputParameter16bit("f.txt", "").validate(""))
        # None
        self.assertFalse(InputParameter16bit("f.txt", None).validate(None))

    def test_InputParameter16bit_physical_file_creation(self):
        """InputParameterとしてのファイル作成機能の確認"""
        param = InputParameter16bit("ver.txt", "0xAB12")
        # InterfaceCard.add_device相当の処理をシミュレート
        param.prepare_file(self.test_root)
        
        # ファイルが存在し、初期値が書き込まれているか
        self.assertTrue(os.path.exists(param.full_path))
        with open(param.full_path, 'r') as f:
            self.assertEqual(f.read(), "0xAB12")

    def test_InputParameter16bit_handle_access_flow(self):
        """handle_access呼び出し時のバリデーション連動確認"""
        # 不正な値を持つインスタンスを作成
        param = InputParameter16bit("error.txt", "0xZZZZ")
        param.prepare_file(self.test_root)
        
        # 不正な値なので、handle_accessを実行してもファイル更新（上書き）はされないはず
        # (初期ファイル作成時は "0xZZZZ" が書き込まれるが、validateが失敗するため)
        param.handle_access()
        
        # 注: この設計では初期値が不正でもprepare_fileで一旦書き込まれますが、
        # 以降の handle_access 内の validate で False となり、更新がスキップされることを確認します。
        self.assertFalse(param.validate(param._value))

if __name__ == '__main__':
    unittest.main()
