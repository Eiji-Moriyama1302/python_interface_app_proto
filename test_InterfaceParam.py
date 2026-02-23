import unittest
import os
import shutil
from InterfaceParam import InputParameter,OutputParameter,Device,InterfaceCard

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

if __name__ == '__main__':
    unittest.main()
