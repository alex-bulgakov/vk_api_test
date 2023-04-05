def set_login_pass(login , password):
    with open('config.txt', 'w') as f:
        f.write(login + '\n')
        f.write(password + '\n')


def get_login_pass():
    with open('config.txt', 'r') as f:
        return f.readlines()
