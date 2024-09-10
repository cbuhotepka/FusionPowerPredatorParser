import os
import shutil

ROOT_PATH = "Z:/"
DIRS_FILE = "C:/dev/move.txt"


class Mover:
    def __init__(self, user_number: int):
        self.user_number = f"blitz{user_number}"
        self.path_imported = os.path.join(ROOT_PATH, self.user_number, "Imported")
        self.path_source = os.path.join(ROOT_PATH, self.user_number, "Source")
        try:
            self.error_dirs = self.__get_error_dirs()
        except Exception as ex:
            print(f"Couldn't get error_dirs: {ex}")
            self.error_dirs = []
        self.found_dirs = []
        self.moved_dirs = set()

    def move(self):
        self._iterate_dirs()
        left_dirs = set(self.error_dirs).difference(self.found_dirs)
        if left_dirs:
            print(f"\n{len(left_dirs)} NOT FOUND DIRS:")
            for dir in left_dirs:
                print(dir)
        print(f"\n{len(self.found_dirs)} DIRS MOVED")

    def cancel(self):
        print("\nRETURNING DIRS:")
        for dir in self.moved_dirs:
            self._move(dir, returning=True)
            print(f"-> {dir}")
        self.moved_dirs.clear()

    def _iterate_dirs(self):
        for base_type in ["combo", "db"]:
            for dir in self._get_dirs(base_type):
                if self._is_error_dir(base_type, dir):
                    self._move(dir)
                    self.moved_dirs.add(dir)

    def _is_error_dir(self, base_type, dir_path) -> bool:
        dir_name = os.path.basename(dir_path)
        dir_name = dir_name.replace(" ", "_")
        for error_name in self.error_dirs:
            if (base_type == "combo" and error_name in dir_name) or error_name == dir_name:
                self.found_dirs.append(error_name)
                return True
        return False

    @staticmethod
    def __get_error_dirs() -> list[str]:
        error_dirs = []
        with open(DIRS_FILE, "r+") as f:
            for line in f:
                error_dir = line.strip().replace(" ", "_")
                if error_dir and error_dir != "_":
                    error_dirs.append(error_dir)
        return error_dirs

    def _get_dirs(self, base_type: str) -> str:
        path = os.path.join(self.path_imported, base_type)
        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):
                yield str(os.path.join(path, item))

    @staticmethod
    def _move(base_path, returning=False):
        print(f"-> {base_path}")
        path_from = str(base_path)
        if not returning:
            path_to = path_from.replace("Imported", "Source")
        else:
            path_from = base_path.replace("Imported", "Source")
            path_to = path_from.replace("Source", "Imported")
        shutil.move(path_from, path_to)


COMMANDS = ["move", "cancel", "exit"]


def main():
    command = input(f"Enter command {COMMANDS}: ")
    if command not in COMMANDS:
        print("Invalid command")
    elif command == "exit":
        raise StopIteration
    elif command == "move":
        mover.move()
    elif command == "cancel":
        mover.cancel()


if __name__ == "__main__":
    user_number = input("Enter user number: ")
    mover = Mover(int(user_number))
    while True:
        main()
