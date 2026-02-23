import unittest
from unittest.mock import MagicMock, patch, call
import os
from InterfaceParam import InterfaceCard

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
    def test_update_status_flow(self, mock_makedirs):
        """update_statusを実行した際、CtrlのメソッドとDeviceのaccessが正しい順序で呼ばれるか"""
        card = InterfaceCard(self.mock_ctrl_class, self.card_dir)
        card.add_device(self.mock_device)
        
        # テスト実行
        card.update_status()
        
        # 呼び出し順序の検証
        # 1. open -> 2. refresh -> 3. device.access -> 4. close
        self.mock_ctrl_instance.open.assert_called_once()
        self.mock_ctrl_instance.refresh.assert_called_once()
        self.mock_device.access.assert_called_once_with(self.mock_ctrl_instance)
        self.mock_ctrl_instance.close.assert_called_once()

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

if __name__ == '__main__':
    unittest.main()
