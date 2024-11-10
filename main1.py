import tkinter as tk
from tkinter import filedialog, ttk
import zipfile
import os
import csv
import subprocess


class ShellEmulator:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.fs_zip_path = self.config['vfs_zip']
        self.log_file = self.config['log_file']
        self.start_script = self.config['start_script']
        self.fs = None
        self.current_path = '/'
        self.load_virtual_filesystem()

    def load_config(self, config_file):
        config = {}
        with open(config_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                config[row[0]] = row[1]
        return config

    def load_virtual_filesystem(self):
        """ Загрузка виртуальной файловой системы из zip-архива """
        self.fs = zipfile.ZipFile(self.fs_zip_path, 'r')

    def execute_command(self, command):
        """ Выполнение команды в эмуляторе """
        if command == "exit":
            self.exit_emulator()
        elif command.startswith("cd "):
            self.change_directory(command[3:])
        elif command == "ls":
            self.list_directory()
        elif command == "who":
            self.show_user()
        elif command.startswith("chmod "):
            self.change_permissions(command[6:])
        elif command.startswith("tail "):
            self.tail_file(command[5:])
        else:
            self.log(f"Неизвестная команда: {command}")

    def list_directory(self):
        """ Команда ls - показать список файлов """
        files = []
        for f in self.fs.namelist():
            if f[:len(self.current_path[1:])] == self.current_path[1:]:
                ff = f[len(self.current_path[1:]):]
                if ff != '':
                    if (len(ff.split('/')) > 1 and list(ff.split('/'))[1] == "") or len(ff.split('/')) == 1:
                        files.append(ff)
        files.sort()
        self.display_output("ls\n" + "\n".join(files))

    def change_directory(self, path):
        """ Команда cd - смена директории """
        print(self.fs.namelist())
        if path == "..":
            self.current_path = '/'.join(self.current_path.split('/')[:-2])
        elif path + "/" in self.fs.namelist():
            self.current_path += path + '/'
        self.display_output(f"cd\nТекущий путь: {self.current_path}")

    def show_user(self):
        """ Команда who - вывод информации о пользователе """
        self.display_output(f"who\nПользователь: user")

    def change_permissions(self, permissions):
        """ Команда chmod - изменение прав доступа """
        self.display_output(
            f"chmod\nПрава доступа изменены на {list(permissions.split())[0]} для файла {self.current_path}{list(permissions.split())[1]}")

    def tail_file(self, filename):
        """ Команда tail - вывод последних строк файла """
        with self.fs.open(filename) as f:
            lines = f.readlines()
            self.display_output('tail\n'+"".join(lines[-10:]))  # Показать последние 10 строк

    def display_output(self, output):
        """ Вывод результата на экран и логирование """
        self.log(output)
        output = "\n".join(list(output.split('\n')[1:]))
        self.text_widget.insert(tk.END, output + "\n")
        self.text_widget.yview(tk.END)

    def log(self, message):
        """ Логирование действия в файл """
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([message])

    def exit_emulator(self):
        """ Завершение работы эмулятора """
        self.root.quit()

    def run(self):
        """ Запуск GUI """
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        self.text_widget = tk.Text(self.root, height=20, width=80)
        self.text_widget.pack(pady=10)

        self.entry = ttk.Entry(self.root, width=80)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_enter)

        self.root.mainloop()

    def on_enter(self, event):
        """ Обработка ввода команды """
        command = self.entry.get()
        self.execute_command(command)
        self.entry.delete(0, tk.END)


if __name__ == "__main__":
    emulator = ShellEmulator('config.csv')
    emulator.run()
