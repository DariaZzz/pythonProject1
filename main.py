import os
import shutil
import zipfile
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

class ShellEmulator:
    def __init__(self, master, username, hostname, zip_path):
        self.master = master
        self.username = username
        self.hostname = hostname
        self.zip_path = zip_path
        self.current_path = '/'
        self.virtual_fs = {}

        self.master.title(f"{self.hostname} - {self.username}'s Shell")
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.input_field = tk.Entry(master)
        self.input_field.pack(padx=10, pady=10)
        self.input_field.bind('<Return>', self.execute_command)

        self.load_virtual_file_system()
        self.prompt()

    def load_virtual_file_system(self):
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            for name in z.namelist():
                self.virtual_fs['/' + name] = z.read(name)

    def prompt(self):
        self.input_field.delete(0, tk.END)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_path}$ ")
        self.text_area.see(tk.END)

    def execute_command(self, event):
        command = self.input_field.get()
        self.text_area.insert(tk.END, f"{command}\n")
        self.input_field.delete(0, tk.END)

        if command.startswith('cd '):
            self.change_directory(command[3:])
        elif command == 'ls':
            self.list_files()
        elif command == 'exit':
            self.master.quit()
        elif command.startswith('mv '):
            self.move_file(command[3:])
        elif command.startswith('echo '):
            self.echo(command[5:])
        elif command.startswith('head '):
            self.head(command[5:])
        else:
            self.text_area.insert(tk.END, "Команда не найдена\n")

        self.prompt()

    def change_directory(self, path):
        if path.startswith('..'):
            while path.startswith('../'):
                path = path[3:]
                if self.current_path != '/':
                    self.current_path = '/'.join(self.current_path.split('/')[:-2]) + '/'
            if path:
                self.current_path = '/'.join(self.current_path.split('/')[:-2]) + '/'
        elif path.count('.') != 0:
            self.text_area.insert(tk.END, "Нет такого каталога\n")
        elif path.startswith('/'):
            if path in self.virtual_fs or path[1:] in self.virtual_fs:
                self.current_path = self.current_path + path
        elif self.current_path + path + '/' in  self.virtual_fs or self.current_path[1:] + path + '/' in self.virtual_fs:
            self.current_path = self.current_path + path + '/'
        elif self.current_path + path in self.virtual_fs or self.current_path[1:] + path in self.virtual_fs:
            self.current_path = self.current_path + path

        else:
            self.text_area.insert(tk.END, "Нет такого каталога\n")

    def list_files(self):
        files = []
        for name in self.virtual_fs.keys():
            if name.count('.') != 0 and\
                name.startswith(self.current_path)\
                and self.current_path.count('/') == name.count('/'):
                if name[len(self.current_path):]:
                    files.append(name[len(self.current_path):])
        self.text_area.insert(tk.END, "\n".join(files) + "\n")

    def move_file(self, args):
        src, dest = args.split()
        if dest.count('.') == 0 and src.count('.') == 1:
            if src[0] == '/':
                src = src.replace(self.current_path, "")
            if dest[-1] != '/':
                dest = dest + '/' + src
            else:
                dest += src
            src = self.current_path + src

            if dest[0] != '/':
                dest = self.current_path + dest
            if src in self.virtual_fs:
                self.virtual_fs[dest] = self.virtual_fs.pop(src)
            else:
                self.text_area.insert(tk.END, "Ошибка перемещения файла\n")

    def echo(self, message):
        self.text_area.insert(tk.END, message + "\n")

    def head(self, filename, n=10):
        content =""
        if filename in self.virtual_fs:
            content = self.virtual_fs[filename].decode('utf-8').splitlines()
            self.text_area.insert(tk.END, "\n".join(content[:10]) + "\n")
        elif self.current_path + filename in self.virtual_fs:
            content = self.virtual_fs[self.current_path + filename].decode('utf-8').splitlines()
            self.text_area.insert(tk.END, "\n".join(content[:10]) + "\n")
        elif self.current_path[1:] + filename in self.virtual_fs:
            content = self.virtual_fs[self.current_path + filename].decode('utf-8').splitlines()
            self.text_area.insert(tk.END, "\n".join(content[:10]) + "\n")
        else:
            self.text_area.insert(tk.END, "Файл не найден\n")


if __name__ == "__main__":
    root = tk.Tk()
    username = simpledialog.askstring("Имя пользователя", "Введите имя пользователя:")
    hostname = simpledialog.askstring("Имя компьютера", "Введите имя компьютера:")
    zip_path = simpledialog.askstring("Путь к архиву", "Введите путь к архиву виртуальной файловой системы:")

    if username and hostname and zip_path:
        shell = ShellEmulator(root, username, hostname, zip_path)
        root.mainloop()
    else:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
