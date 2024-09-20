import unittest


loader = unittest.TestLoader()
suite = loader.discover(start_dir="./bdl_commands_test", pattern="*_test.py")

runner = unittest.TextTestRunner()
runner.run(suite)
