import unittest
import mainn
from unittest.mock import Mock

class TestCamera(unittest.TestCase): 
    '''класс для тестирования методов класса Camera'''                                                                                                                                                                                                                                                                        
    def test_apply(self):
        self.assertIs(mainn.Camera.apply('Player Sprite(in 1 groups'), 'rect(38, 576, 22, 32)')
        mock = Mock()
        mock.return_value = 'rect(38, 576, 22, 32)'
        mock()
        
    def test_reverse(self):
        self.assertIs(mainn.Camera.reverse((400, 320)), 400, 480)
        mock = Mock()
        mock.return_value = 400, 480
        mock()
    
    def test_camera_config(self):
        self.assertIs(mainn.Camera.camera_config((0, 0)), 0 -160)
        mock = Mock()
        mock.return_value = 0, -160, 3200, 800
        mock()

if __name__ == '__main__':
    unittest.main()