import unittest
from unittest.mock import MagicMock, patch, call
import os
from InterfaceParam import InterfaceCard, BaseParameter

class TestInterfaceCard(unittest.TestCase):

    def setUp(self):
        # 共通で使用するモックの作成
        self.mock_ctrl_class = MagicMock()
        self.mock_ctrl_instance = self.mock_ctrl_class.return_value
        self.card_dir = "test_card_dir"
        
        # Deviceのモック
        self.mock_device = MagicMock()
        self.mock_device.directory_name = "device_A"
        self.mock_device.parameters = [MagicMock(), MagicMock()]

    @patch('os.makedirs')
    @patch('os.path.join')
    def test_init_with_devices(self, mock_join, mock_makedirs):
        """初期化時にDevicesが渡された場合、正しくadd_deviceが呼ばれるか"""
        mock_join.return_value = "joined/path"
        devices = [self.mock_device]
        
        # インスタンス化
        card = InterfaceCard(self.mock_ctrl_class, self.card_dir, Devices=devices)
        
        # アサーション
        self.assertEqual(card.card_directory, self.card_dir)
        self.assertIn(self.mock_device, card.devices)
        self.mock_ctrl_class.assert_called_once()  # ctrl = InterfaceCtrl() が呼ばれたか
        
        # add_device内の処理が走っているか
        mock_makedirs.assert_called_with("joined/path", exist_ok=True)
        for param in self.mock_device.parameters:
            param.prepare_file.assert_called_with("joined/path")

    @patch('os.makedirs')
    @patch('os.path.join')
    def test_add_device_flow(self, mock_join, mock_makedirs):
        """add_deviceを実行した際、open/closeが正しく呼ばれるか"""
        card = InterfaceCard(self.mock_ctrl_class, self.card_dir)
        
        # 1. ここで初期化時の呼び出しをリセットする
        self.mock_ctrl_instance.open.reset_mock()
        self.mock_ctrl_instance.close.reset_mock()
        
        # 2. テスト実行
        card.add_device(self.mock_device)
        
        # 3. add_device内で呼ばれた1回を検証
        self.mock_ctrl_instance.open.assert_called_once()
        self.mock_ctrl_instance.close.assert_called_once()
        
    @patch('os.makedirs')
    def test_update_status_flow(self, mock_makedirs):
        """update_statusを実行した際、呼び出し回数が累計2回になることを確認"""
        card = InterfaceCard(self.mock_ctrl_class, self.card_dir)

        # 初期化時の分をリセット
        self.mock_ctrl_instance.open.reset_mock()
        self.mock_ctrl_instance.close.reset_mock()
        self.mock_ctrl_instance.refresh.reset_mock()
        
        # 1回目: add_deviceで open/close が呼ばれる
        card.add_device(self.mock_device)
        
        # 2回目: update_statusを実行
        card.update_status()
        
        # 呼び出し回数の検証 (累計 2回)
        self.assertEqual(self.mock_ctrl_instance.open.call_count, 2)
        self.assertEqual(self.mock_ctrl_instance.close.call_count, 2)
        
        # update_status固有の処理は1回だけ呼ばれているはず
        self.mock_ctrl_instance.refresh.assert_called_once()
        self.mock_device.access.assert_called_once_with(self.mock_ctrl_instance)

    @patch('os.makedirs')
    @patch('os.path.join')
    def test_add_device_creates_directories_and_files(self, mock_join, mock_makedirs):
        """add_deviceがディレクトリ作成とパラメータの準備を正しく行うか"""
        mock_join.return_value = "fake/path/device_A"
        card = InterfaceCard(self.mock_ctrl_class, self.card_dir)
        
        card.add_device(self.mock_device)
        
        # パス結合が正しい引数で呼ばれたか
        mock_join.assert_called_with(self.card_dir, self.mock_device.directory_name)
        # ディレクトリ作成が呼ばれたか
        mock_makedirs.assert_called_with("fake/path/device_A", exist_ok=True)
        # 各パラメータのファイル準備が呼ばれたか
        for param in self.mock_device.parameters:
            param.prepare_file.assert_called_with("fake/path/device_A")


class TestBaseParameter(unittest.TestCase):
    """BaseParameterクラスの新メソッドに対するテスト"""

    def setUp(self):
        self.mock_ctrl = MagicMock()
        # テスト用の validator: 正の整数の場合のみ True
        self.validator = lambda x: int(x) > 0
        self.mock_input = MagicMock()
        self.mock_output = MagicMock()
        
        self.param = BaseParameter(
            filename="test_param.txt",
            value=100,
            validator_func=self.validator,
            input_func=self.mock_input,
            output_func=self.mock_output
        )

    def test_get_processed_input(self):
        """入力値が正しく1行目のみ抽出・文字列化されるか"""
        # 正常系: 改行を含む文字列
        self.mock_input.return_value = "200\nsecond_line"
        result = self.param._get_processed_input(self.mock_ctrl)
        self.assertEqual(result, "200")

        # 正常系: 単一の値
        self.mock_input.return_value = 500
        result = self.param._get_processed_input(self.mock_ctrl)
        self.assertEqual(result, "500")

        # 異常系: None
        self.mock_input.return_value = None
        result = self.param._get_processed_input(self.mock_ctrl)
        self.assertIsNone(result)

    def test_apply_update(self):
        """内部状態の更新とoutput_funcの呼び出しが正しく行われるか"""
        new_val = "300"
        self.param._apply_update(self.mock_ctrl, new_val)

        # _value が更新されていること
        self.assertEqual(self.param._value, "300")
        # output_func が正しい引数で呼ばれていること
        self.mock_output.assert_called_once_with(self.mock_ctrl, "300")

    def test_handle_access_always_with_same_value(self):
        """値が前回と同じ(100)でも、更新・通知処理が走ることを確認"""
        self.param._value = "100"
        self.mock_input.return_value = "100"
        
        # 実行
        self.param.handle_access_always(self.mock_ctrl)

        # バリデーションが通れば、値が同じでも output_func が呼ばれるはず
        self.mock_output.assert_called_once_with(self.mock_ctrl, "100")

    def test_handle_access_always_invalid_value(self):
        """バリデーションに失敗した場合は、更新・通知が走らないことを確認"""
        self.param._value = "100"
        self.mock_input.return_value = "-50"  # 0以下なのでバリデーション失敗
        
        # 実行
        self.param.handle_access_always(self.mock_ctrl)

        # output_func は呼ばれない
        self.mock_output.assert_not_called()
        # _value も更新されない
        self.assertEqual(self.param._value, "100")

    def test_handle_access_always_none_input(self):
        """入力がNoneの場合は処理を中断することを確認"""
        self.mock_input.return_value = None
        
        self.param.handle_access_always(self.mock_ctrl)

        self.mock_output.assert_not_called()

if __name__ == '__main__':
    unittest.main()
