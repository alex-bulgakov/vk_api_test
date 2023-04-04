import threading
import time
import tkinter as tk

from PIL import Image, ImageTk

from auth import vk_auth
from lib import stop_thread, get_groups, is_searching, lock, start_search
from status import get_status, set_status

vk = None
group_checkboxes = []
search_gif = None
gif_item = None


def draw_checkboxes(groups, inner_frame, bg_color, fg_color):
    global group_checkboxes
    check_row = 0
    for group in groups:
        group_checkboxes.append((group["name"], group["id"], tk.BooleanVar()))
    for checkbox in group_checkboxes:
        tk.Checkbutton(inner_frame, text=checkbox[0], variable=checkbox[2], bg=bg_color, fg=fg_color).grid(
            row=check_row, column=3, sticky='w', padx=5)
        check_row += 1


def push_auth(login, password, frame, bg_color, fg_color):
    global vk
    if vk:
        set_status('Авторизация уже выполнена')
        return
    vk = vk_auth(login, password)
    draw_checkboxes(get_groups(vk), frame, bg_color, fg_color)



def draw_window():
    # Создание графического интерфейса

    button_bg_color = '#101010'
    button_color = 'white'
    canvas_color = '#2d2d2d'

    root = tk.Tk()
    root.title('VK Поиск')

    # Определяем размер экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Вычисляем размер окна
    window_width = screen_width // 2
    window_height = screen_height // 2

    # Вычисляем координаты окна, чтобы оно отображалось по центру экрана
    x_position = screen_width // 4
    y_position = screen_height // 4

    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_position, y_position))
    print('Root ' + str(root.winfo_width()) + 'x' + str(root.winfo_height()))


    # # создаем фрейм для canvas и полосы прокрутки
    frame = tk.Frame(root, bg='#222222')


    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.pack(expand=True, fill='both')

    # создаем canvas и добавляем его на фрейм
    canvas = tk.Canvas(frame, bg=canvas_color)
    canvas.grid(row=0, column=0, sticky="nsew")

    canvas.config(width=frame.winfo_width(), height=frame.winfo_height())


    # добавляем полосу прокрутки на фрейм
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.set(1, 1)

    # создаем фрейм в canvas
    inner_frame = tk.Frame(canvas, bg=canvas_color, padx=10, pady=10)
    canvas.create_window((5, 5), window=inner_frame, anchor="nw")

    # Поля ввода логина и пароля
    login_label = tk.Label(inner_frame, text='Логин', bg=canvas_color, fg=button_color)
    login_label.grid(row=0, column=0)
    login_entry = tk.Entry(inner_frame)
    login_entry.grid(row=0, column=1)

    password_label = tk.Label(inner_frame, text='Пароль', bg=canvas_color, fg=button_color)
    password_label.grid(row=1, column=0)
    password_entry = tk.Entry(inner_frame, show='*')
    password_entry.grid(row=1, column=1)


    # Кнопка авторизации
    auth_button = tk.Button(inner_frame, text='Войти', command=lambda: push_auth(login_entry.get(), password_entry.get(), inner_frame, canvas_color, '#888888'), bg=canvas_color, fg=button_color)
    auth_button.grid(row=0, column=2, sticky='w')

    # Дата поиска
    start_date_label = tk.Label(inner_frame, text='Искать до даты', bg=canvas_color, fg=button_color)
    start_date_label.grid(row=2, column=0)
    start_date_entry = tk.Entry(inner_frame)
    start_date_entry.grid(row=2, column=1)

    # Поле ввода поиска и кнопка поиска
    search_label = tk.Label(inner_frame, text='Поиск', bg=canvas_color, fg=button_color)
    search_label.grid(row=3, column=1)
    search_entry = tk.Entry(inner_frame)
    search_entry.grid(row=3, column=1)

    # search_button = tk.Button(inner_frame, text='Поиск', command=lambda: start_search(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
    search_button = tk.Button(inner_frame, text='Поиск', command=lambda: start_search(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
    search_button.grid(row=4, column=1)
    # search_button1 = tk.Button(inner_frame, text='Поиск не в фоне', command=lambda: search_and_save(vk, group_checkboxes, search_entry.get(), start_date_entry.get()), bg=canvas_color, fg=button_color)
    # search_button1.grid(row=5, column=1)

    # кнопка остановить поиск
    search_button1 = tk.Button(inner_frame, text='Остановить поиск', command=stop_thread, bg=canvas_color, fg=button_color)
    search_button1.grid(row=5, column=1)


    def update_label(label):
        while True:
            label.configure(text=get_status())
            time.sleep(1)

    # поле с информацией о ходе процесса
    status_label = tk.Label(frame, bg=canvas_color, fg='white')
    status_label.grid(row=1, column=0, sticky=tk.S+tk.W)
    root.rowconfigure(1, weight=1)

    thread = threading.Thread(target=update_label, args=[status_label])
    thread.start()

    gif_canvas = tk.Canvas(inner_frame, width=100, height=100)
    gif_canvas.grid(row=7, column=1)

    def animate_gif(image_file):
        gif_canvas.grid_forget()
        # открываем gif файл и получаем первый кадр
        gif = Image.open(image_file)
        current_frame = 0
        frames = gif.n_frames

        # пока есть кадры
        while True:
            status = get_status()
            if status == 'Начинаем поиск':
                gif_canvas.grid(row=7, column=1)
                # получаем текущий кадр
                gif.seek(current_frame)
                frame = gif.convert('RGBA')
                frame = frame.resize((gif_canvas.winfo_width(), gif_canvas.winfo_height()), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(frame)

                # отображаем текущий кадр на холсте
                gif_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                gif_canvas.update()

                # переходим к следующему кадру
                current_frame += 1
                if current_frame == frames:
                    current_frame = 0

                # задержка между кадрами
                try:
                    delay = gif.info['duration']
                    canvas.after(delay)
                except KeyError:
                    canvas.after(100)
            elif status == 'Готово' or status == 'Поиск прерван':
                gif_canvas.grid_forget()



            # проверка на остановку анимации
            # if not canvas.animating:
            #     break

    gif_thread = threading.Thread(target=animate_gif, args=['searching.gif'])
    gif_thread.start()


    # устанавливаем минимальный размер фрейма с виджетами
    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    root.mainloop()
