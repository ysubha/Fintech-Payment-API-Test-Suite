import configparser


def get_properties(section, label):
    config = configparser.ConfigParser()
    config.read('C:\\Users\Subha\PycharmProjects\Mini Fintech Payment & Order System\properties.ini')
    return config[section][label]
