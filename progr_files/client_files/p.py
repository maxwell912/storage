def _log_find(key):
    import re
    reg = r'.* add \((.*)\) key: {} value: .*'.format(key)
    match = None
    with open('client_log') as log:
        for note in log:
            i = re.match(reg, note)
            if i is not None:
                match = i
    if match is None:
        return None
    ip = match.group(1).split(', ')
    print(ip[0][1:-1], int(ip[1]))


if __name__ == '__main__':
    _log_find('1')