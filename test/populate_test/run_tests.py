import unittest
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
start_dir = os.path.join(current_dir, 'bdl_commands_test')
loader = unittest.TestLoader()
suite = loader.discover(start_dir=start_dir, pattern="*_test.py")

runner = unittest.TextTestRunner()
runner.run(suite)
