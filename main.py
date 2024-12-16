import tarfile
import sys
import re
import json
from os.path import isfile
from pathlib import Path
from tkinter import Tk, WORD, END, Entry, Button
from tkinter.constants import LEFT, BOTH, RIGHT
from tkinter.scrolledtext import ScrolledText


class SH:
    def __init__(self, pcname, systempath):
        self.root = Tk()
        self.pc_name = pcname
        self.system_path = systempath
        self.working_directory = Path('/')
        self.file_system = {}
        self.files = {}
        self.loadsys(systempath)
        self.show_display()
        self.permissions = {}

    def printline(self,
                  line: str) -> None:

        self.command_output.config(state='normal')
        self.command_output.insert(END, line)
        self.command_output.config(state='disabled')

    def loadsys(self,
                file_system_archive: str) -> None:

        if not tarfile.is_tarfile(file_system_archive):
            self.command_output.insert(END, 'Ошибка: Архив .tar не найден\n')
            return

        with tarfile.open(file_system_archive, 'r') as tar:
            files = tar.getmembers()
            for member in files[1:]:
                path = Path(member.path.replace(files[0].path + '/', '/'))
                folder, file = path.parent, path.name
                self.file_system.setdefault(folder, list()).append(file)
                if member.isfile():
                    self.files[path] = member

    def display_prompt(self) -> None:
        self.printline(f'{self.pc_name}@vsh:{self.working_directory.as_posix()}$ ')

    def show_display(self) -> None:
        self.root.title(f'{self.pc_name}: Командная строка')
        self.command_output = ScrolledText(self.root, wrap=WORD, height=12, width=80)
        self.command_output.configure(font=('Arial', 13))
        self.command_output.pack(padx = 10, pady = 10)

        self.command_input = Entry(self.root, width=60)
        self.command_input.configure(font=('Arial', 14))
        self.command_input.pack(side=LEFT, padx=(10, 0))

        self.submit_button = Button(self.root, text='Ввод', width=15, command=self.handle_command)
        self.submit_button.configure(font=('Arial', 13))
        self.submit_button.pack(side=RIGHT, padx=(10, 0))

        self.display_prompt()

    def __exit(self):
        self.root.quit()

    def get_path(self,
                 directory_path):

        if directory_path.startswith('/'):
            search_directory = Path(directory_path)
        elif directory_path == '..' or directory_path == '../':
            search_directory = self.working_directory.parent
        elif directory_path == '.' or directory_path == './':
            search_directory = self.working_directory
        elif directory_path.startswith('..'):
            return self.get_path(self.working_directory.parent.as_posix() + directory_path[2:])
        elif directory_path.startswith('./'):
            return self.get_path((self.working_directory / directory_path[2:]).as_posix())
        else:
            search_directory = self.working_directory / directory_path

        return search_directory

    def get_content(self,
                    search_directory):

        if search_directory in self.file_system:
            content = '    '.join(self.file_system[search_directory])
        else:
            content = f'cannot access "{search_directory.as_posix()}": No such file or directory'

        return content

    def set_dir(self,
                new_working_directory: Path) -> None:

        if new_working_directory in self.file_system:
            self.working_directory = new_working_directory
        else:
            self.printline(f'{new_working_directory.as_posix()}: No such file or directory\n')

    def __ls(self,
             directories):

        contents = list()
        for directory in directories:
            search_directory = self.get_path(directory)
            contents.append(f'{directory}: {self.get_content(search_directory)}')
        if not contents:
            contents.append(
                f'{self.working_directory.as_posix()}: {self.get_content(self.working_directory)}')

        for content in contents:
            self.printline(content + '\n')

    def __cd(self,
             directories):

        if len(directories) > 1:
            self.printline('too many arguments\n')
            return

        if len(directories) == 0:
            search_directory = Path('/')
        else:
            search_directory = self.get_path(directories[0])

        self.set_dir(search_directory)

    def __cat(self,
              files_pathes):

        if not files_pathes:
            self.printline('Usage: wc [FILE]...\n')
            return

        with tarfile.open(self.system_path, 'r') as tar:
            for file_path in files_pathes:
                path = self.get_path(file_path)
                if path in self.files:
                    file_info = self.files[path]
                    file_text = tar.extractfile(file_info).read().decode()
                    self.printline(file_text)
        self.printline("\n")

    def __find(self, target):
        for key, val in self.file_system.items():
            for finding in val:
                try:
                    if target[0] in finding:
                        self.printline(f'{key} {finding}' + '\n')
                except:
                    pass

    def __chmod(self, args):

        if len(args) != 2:
            self.printline('Аргументов должно быть 2\n')
            return
        filename = args[0]
        newrule = args[1]
        if not re.match(r'^[rwx-]{9}$', newrule):
            self.printline('Неверный формат. Используйте rwxr-xr-x формат\n')
            return

        with tarfile.open(self.system_path, 'r') as tar:
            path = self.get_path(filename)
            if path in self.files:
                file_info = self.files[path]
                self.permissions[file_info] = newrule
                self.printline(f'Права {newrule} для {filename} успешно установлены!\n')
                print(self.permissions)
            else:
                self.printline(f'Файл {filename} не найден\n')
        pass

    def execute_command(self,
                        command_line: str) -> None:

        self.printline(command_line + '\n')
        if command_line:
            command_split = command_line.split()
            command, args = command_split[0], command_split[1:]

            if command == 'ls':
                self.__ls(args)
            elif command == 'cd':
                self.__cd(args)
            elif command == 'exit':
                self.__exit()

            elif command == 'cat':
                self.__cat(args)
            elif command == 'find':
                self.__find(args)

            elif command == 'chmod':
                self.__chmod(args)

            else:
                self.printline('command not found\n')

        self.display_prompt()

    def handle_command(self) -> None:
        command_line = self.command_input.get().strip()
        self.command_input.delete(0, END)

        self.execute_command(command_line)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('Использовать: python main.py <json_data> ')
        sys.exit(1)

    json_file = sys.argv[1]
    with open(json_file, 'r') as file:
        data = json.load(file)
    PC_name = data['computer_name']
    system_path = data['archive_path']
    sh = SH(PC_name, system_path)
    sh.run()
