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
        self.fs = zipfile.ZipFile(self.fs_zip_path, 'r')

    def execute_command(self, command):
        command = command.split('> ')[1]
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
        if path == "..":
            self.current_path = '/'.join(self.current_path.split('/')[:-2])
        elif path + "/" in self.fs.namelist():
            self.current_path += path + '/'
        self.display_output(f"cd\nТекущий путь: {self.current_path}")

    def show_user(self):
        self.display_output(f"who\nПользователь: user")

    def change_permissions(self, permissions):
        self.display_output(
            f"chmod\nПрава доступа изменены на {list(permissions.split())[0]} для файла {self.current_path}{list(permissions.split())[1]}")

    def tail_file(self, filename):
        with self.fs.open(filename) as f:
            lines = f.readlines()
            self.display_output('tail\n'+"".join(lines[-10:]))

    def display_output(self, output):
        self.log(output)
        output = "\n".join(list(output.split('\n')[1:]))
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.current_path + "> " + output + "\n")
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.yview(tk.END)

    def log(self, message):
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([message])

    def exit_emulator(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        self.text_widget = tk.Text(self.root, height=20, width=80, state=tk.DISABLED)
        self.text_widget.pack(pady=10)

        self.entry = ttk.Entry(self.root, width=80)
        self.entry.pack(pady=5)
        self.entry.insert(0, f"{self.current_path}> ")
        self.entry.bind('<Return>', self.on_enter)

        self.root.mainloop()

    def on_enter(self, event):
        command = self.entry.get()
        self.execute_command(command)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{self.current_path}> ")

if __name__ == "__main__":
    emulator = ShellEmulator('config.csv')
    emulator.run()
