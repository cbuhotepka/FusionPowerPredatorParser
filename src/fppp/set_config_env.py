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
        p = Path(__file__).parent / 'CONFIG.env'
        f = p.open('w', encoding='utf-8')
        for conf in self.config_list:
            f.write(conf + '\n')
        f.close()


def set_env():
    variables = ['PARSING_DISK_NAME', 'USER_NAME', 'USER_PASSWORD', 'SOURCE_DISK_NAME', 'SERVER_PORT_FIX',
                 "TOO_MANY_FILES_TRESHOLD"]
    config = Config(*variables)
    config.input_config()
    config.save_config()


if __name__ == '__main__':
    set_env()
