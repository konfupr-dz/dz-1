import unittest
from main import SH
from pathlib import Path


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.shell = SH('PC', 'system.tar')

    def get_command_output(self, command: str) -> str:
        start_line_index = self.shell.command_output.index("insert linestart")
        self.shell.execute_command(command)

        return self.shell.command_output.get(start_line_index, "end-2c")

    def test_ls_root(self):
        output = self.get_command_output('ls')
        self.assertIn('4e4nya', output)


    def test_ls_sec(self):
        output = self.get_command_output('ls 4e4nya')
        self.assertIn('js', output)
        self.assertIn('style.css', output)

    def test_cd_fir(self):
        self.shell.execute_command('cd 4e4nya')
        self.assertEqual(self.shell.working_directory.as_posix(), '/4e4nya')

    def test_cd_sec(self):
        self.shell.execute_command('cd 4e4nya/js')
        self.assertEqual(self.shell.working_directory.as_posix(), '/4e4nya/js')

    def test_cat_fir(self):
        output = self.get_command_output('cat test.txt')
        self.assertIn('\n6\r\n2\r\n10 20\r\n12 50\r\n25 43\r\n38 70\r\n40 51\r\n55 70\n', output)

    def test_cat_sec(self):
        output = self.get_command_output('cat tit.txt')
        self.assertIn('\nprivet\r\nbbebe\n', output)

    def test_find_fir(self):
        output = self.get_command_output('find tit.txt')
        self.assertIn('\ tit.txt', output)

    def test_find_sec(self):
        output = self.get_command_output('find a')
        self.assertIn('\ 4e4nya\n\\4e4nya images\n\\4e4nya\\images 1755654839_0_230_3232_2048_1920x0_80_0_0_89d58e36fde2ba3ce1f3ac4cc24d549c.jpg\n\\4e4nya\\images main.jpg\n\\4e4nya\\images scale_1200.webp\n\\4e4nya\\images way1.jpg\n\\4e4nya\\images way2.jpg\n\\4e4nya\\images way3.jpg\n\\4e4nya\\images way4.jpg\n\\4e4nya\\images way5.jpg\n\\4e4nya\\images way6.jpg\n\\4e4nya\\images way7.jpg\n\\4e4nya\\images way8.jpg\n', output)

    def test_chmod_fir(self):
        output = self.get_command_output('chmod tit.txt bebra')
        self.assertIn('Неверный формат. Используйте rwxr-xr-x формат\n', output)

    def test_chmod_sec(self):
        output = self.get_command_output('chmod tit.txt rwxr-xr-x')
        self.assertIn('Права rwxr-xr-x для tit.txt успешно установлены!', output)

if __name__ == '__main__':
    unittest.main()