from src.console import Console
import configparser
import threading
import tarfile

class BashFake:
    path = "/"
    config = {
        "file_system": "",
        "start_script": "",
    }

    def __init__(self):
        self.console = Console(self.cmd_processing)

        # Load config
        config_parser = configparser.ConfigParser()
        config_parser.read('./config.ini')
        self.config["file_system"] = config_parser["config"]["file_system"]
        self.config["start_script"] = config_parser["config"]["start_script"]

        # Set current path
        self.path = self.config["file_system"].replace(".tar", "") + "/"

    # --- Commands processing ---

    def _ls(self, append_path=""):
        path = self.get_path(append_path)
        elems = set()
        with tarfile.open(self.config["file_system"], "r") as tar:
            for member in tar.getmembers():
                if not member.name.startswith(path):
                    continue
                elems.add(member.name.split("/")[path.count("/")])     

        return "\n".join(elems)

    def _cd(self, path):
        self.path = self.path.replace("//", "/")
        if type(path) != list:
            path = path.split("/")
        if path[0] == "" and len(path) > 1:
            self.path = "/".join(self.path.split("/")[:2]) + "/"
            return self._cd(path[1:])
        if path[0] == "":
            return

        if path[0] == "..":
            if self.path == "./file_system/":
                return self._cd(path[1:])
            self.path = "/".join(self.path.split("/")[:-2]) + "/"
            return self._cd(path[1:])
        elif path[0] == ".":
            return self._cd(path[1:])
        else:
            with tarfile.open(self.config["file_system"], "r") as tar:
                for member in tar.getmembers():
                    if member.name == self.path + "/".join(path) and member.isdir():
                        break
                else:
                    return "No such directory"

            self.path += "/".join(path) + "/"
            self.path = self.path.replace("//", "/")

    def _tail(self, path):
        path = self.get_path(path)[:-1]
        with tarfile.open(self.config["file_system"], "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isfile():
                    break
            else:
                return "No such file"

            with tar.extractfile(member) as f:
                lines = f.readlines()
                lines = [line.decode("utf-8") for line in lines]
                return "".join(lines[-min(len(lines), 10):])

    def _whoami(self):
        return "user"  # Здесь можно вернуть текущее имя пользователя

    def _mkdir(self, dirname):
        if not dirname:
            return "mkdir: missing operand"  # Возвращаем сообщение об ошибке

        path = self.get_path(dirname)

        # Проверка, существует ли уже директория
        with tarfile.open(self.config["file_system"], "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isdir():
                    return f"mkdir: cannot create directory '{dirname}': File exists"

        # Здесь необходимо реализовать логику создания директории в архиве .tar

        return f"Directory '{dirname}' created."

    # --- Class methods ---

    def get_path(self, path):
        path = path.split("/")
        result_path = self.path
        if path[0] == "" and len(path) > 1:
            result_path = "./file_system/"
            path = path[1:]
        for elem in path:
            if elem == "..":
                result_path = "/".join(result_path.split("/")[:-2]) + "/"
            elif elem == ".":
                continue
            else:
                result_path += elem + "/"
            result_path = result_path.replace("//", "/")
        return result_path

    def cmd_processing(self, command):
        command = command.split(" ")
        match command[0]:
            case "ls":
                self.console.print(self._ls(command[1] if len(command) > 1 else ""))
            case "cd":
                error = self._cd(command[1])
                if error:
                    self.console.print(error)

                new_path = self.path.replace(
                    self.config["file_system"].replace(".tar", ""), "")
                self.console.set_path(new_path)
            case "tail":
                self.console.print(self._tail(command[1]))
            case "whoami":
                self.console.print(self._whoami())
            case "mkdir":
                self.console.print(self._mkdir(command[1] if len(command) > 1 else ""))
            case "exit":
                self.console.print("Exiting...")
                exit(0)  # Завершение программы с кодом 0 (успешное завершение)
            case _:
                self.console.print("Unknown command")

        self.console.insert_prompt()
    
    def run_start_script(self):
        if self.config["start_script"]:
            script = open(self.config["start_script"], "r")
            self.console.insert_prompt()
            for line in script:
                line = line.strip()
                self.console.print(line)
                self.cmd_processing(line)
            script.close()
    
    def run(self):
        start_cmds = threading.Thread(target=self.run_start_script)
        start_cmds.start()  

        self.console.run()

if __name__ == "__main__":
    not_bash = BashFake()
    not_bash.run()
