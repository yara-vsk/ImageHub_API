import re


def files_checker(files):
    for file in files:
        if not re.match(r'.*\.(png|jpg)$', file.name):
            return False
    return True