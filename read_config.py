def get_config():
    result = []
    try:
        with open('config.txt', 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            for line in lines:
                result.append(line.split(' ')[1].strip())
            return result
    except FileNotFoundError:
        print('Не найден конфигурационный файл config.txt')
        return []
