import pickle


def save_api(api):
    with open('api.txt', 'wb') as f:
        pickle.dump(api, f)


def get_api():
    with open('api.txt', 'rb') as f:
        return pickle.load(f)
