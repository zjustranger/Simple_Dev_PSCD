import os

def load_config(filename='conf.ini', special_encoding='utf-8'):
    '''
    load all configurations and return a dict
    the default file is current_folder/conf.ini
    format is like below(only lines with '=' will be recognized as parameters):
    ===================================
    [Video]
    Window_width=1920
    Window_height=1080
    Sound_on=1

    [System]
    1Database = Sqlite3

    [Configuration]
    logging = True
    ====================================
    '''
    dict = {}
    config_file = open(filename, 'r', encoding=special_encoding)
    lines = config_file.readlines()
    for line in lines:
        if line:
            line = line.strip()  # delete the blanks in line begin and end.
            try:
                content = line.split('=')   # split parameter and value
                content = [i.strip() for i in content]  # delete the blanks
                parameter = content[0]
                value = content[1]
            except:
                continue
            try:
                add_command = 'dict["{}"]={}'.format(parameter, value)
                exec(add_command)
            except:
                try:
                    add_command = 'dict["{}"]="{}"'.format(parameter, value)    #if value cannot been assign to paramater directly, save as string.
                    exec(add_command)
                except:
                    pass
        else:
            pass
    config_file.close()
    return dict

if __name__ == '__main__':
    configs = load_config()
    print(configs)
    print(load_config.__doc__)
