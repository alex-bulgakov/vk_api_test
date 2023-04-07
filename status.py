


def set_status(msg):
    with open('status.txt', 'w', encoding='cp1251') as f:
        f.write(msg)


def get_status():
    with open('status.txt', 'r', encoding='cp1251') as f:
        return f.readline()
