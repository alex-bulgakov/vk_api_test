
def set_status(msg):
    with open('status.txt', 'w') as f:
        f.write(msg)


def get_status():
    with open('status.txt', 'r') as f:
        return f.readline()
