from pathlib import Path


class Config:

    def __init__(self, *args):
        self.varaibals = args
        self.config_list = []

    def input_config(self):
        for var in self.varaibals:
            value = input(f"{var}=")
            self.config_list.append(f"{var}={value}")

    def save_config(self):
        p = Path('CONFIG.env')
        f = p.open('w', encoding='utf-8')
        for conf in self.config_list:
            f.write(conf + '\n')
        f.close()


if __name__ == '__main__':
    # Example
    variables = ['PARSING_DISK_NAME', 'USER_NAME', 'USER_PASSWORD', 'SOURCE_DISK_NAME', 'SERVER_PORT_FIX', "TOO_MANY_FILES_TRESHOLD"]
    config = Config(*variables)
    config.input_config()
    config.save_config()
