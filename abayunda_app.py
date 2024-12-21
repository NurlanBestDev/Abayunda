import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import bcrypt
import webbrowser

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, font=("Arial", 10), background="white", relief="solid", borderwidth=1)
        label.pack()
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None

def info(event=None):
    about_window = tk.Toplevel()
    about_window.title("Об Abayunda")
    about_window.geometry("650x350")
    about_window.config(bg="#ffc83d")
    image = Image.open("Abayunda.png")
    image = image.resize((565, 125))
    logo = ImageTk.PhotoImage(image)
    about_window.logo = logo
    tk.Label(about_window, image=logo, bd=2, relief="solid").pack(pady=25)
    info_text = """Abayunda — это дружелюбная, умная обучающая система.\nПрограмма основана на методе интервальных повторений."""
    info_label = tk.Label(about_window, bg="white", text=info_text, fg="black", font=("Arial", 12, "bold"), justify=tk.CENTER, anchor="center", bd=4, relief="ridge")
    info_label.pack(pady=10)
    frame = tk.Frame(about_window, bg="#ffc83d", bd=4, relief="ridge")
    frame.pack(pady=10)
    version_label = tk.Label(frame, bg="white", text="Версия: 1.0", fg="black", font=("Arial", 12))
    version_label.pack(side=tk.LEFT)
    def open_guide():
        webbrowser.open("https://docs.google.com/document/d/1F5AOhw2jYFbQ36OS2fmmGxWvyThgdH2t9XpuoQOKZFg/edit?usp=sharing")
    guide_label = tk.Label(frame, bg="white", text="Руководство", font=("Arial", 12), fg="blue", cursor="hand2")
    guide_label.pack(side=tk.LEFT)
    guide_label.bind("<Button-1>", lambda e: open_guide())
    tk.Button(about_window, bg="white", text="ОК", font=("Arial", 10), command=about_window.destroy, width=5).pack(pady=10)

def login(event=None):
    login_window = tk.Toplevel()
    login_window.title("Вход")
    login_window.geometry("275x240")
    login_window.config(bg="#ffc83d")
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM logins;")
    login_count = cursor.fetchone()[0]
    if login_count == 0:
        registration()
        login_window.destroy()
        return
    tk.Label(login_window, text="Имя пользователя/E-mail:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    login_entry = tk.Entry(login_window, font=("Arial", 10))
    login_entry.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(login_window, text="Пароль:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    password_entry = tk.Entry(login_window, font=("Arial", 10), show="*")
    password_entry.pack(fill=tk.X, padx=5, pady=5)
    def handle_login():
        global current_user
        username = login_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите имя пользователя и пароль.")
            return
        cursor.execute("SELECT * FROM logins WHERE user_name = %s OR email = %s", (username, username))
        user = cursor.fetchone()
        if user:
            cursor.execute("SELECT password FROM passwords WHERE login_id = %s", (user[0],))
            stored_password = cursor.fetchone()[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                current_user = user[1]
                root.title(f"{current_user} - Abayunda")
                login_id = user[0]
                cursor.execute("""SELECT d.deck_name, p.new_cards, p.learn_cards, p.repeat_cards FROM decks d LEFT JOIN progress p ON d.deck_id = p.deck_id WHERE d.login_id = %s""", (login_id,))
                decks = cursor.fetchall()
                for item in deck_list.get_children():
                    deck_list.delete(item)
                for deck in decks:
                    deck_name, new_cards, learn_cards, repeat_cards = deck
                    deck_list.insert("", "end", values=(deck_name, new_cards, learn_cards, repeat_cards))
                if current_user == "n" or current_user == "v":
                    admin_menu = tk.Menu(menu_bar, tearoff=0)
                    admin_menu.add_command(label="Режим админа", command=admin_mode)
                    menu_bar.add_cascade(label="Админ", menu=admin_menu)
                cursor.close()
                connection.close()
                login_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный пароль.")
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден.")
    tk.Button(login_window, text="Войти", font=("Arial", 10), bg="white", command=handle_login).pack(pady=10)
    tk.Button(login_window, text="Зарегистрироваться", font=("Arial", 10), bg="white", command=lambda:(registration(), login_window.destroy())).pack(pady=5)

def registration():
    registration_window = tk.Toplevel()
    registration_window.title("Регистрация")
    registration_window.geometry("275x385")
    registration_window.config(bg="#ffc83d")
    tk.Label(registration_window, text="Имя пользователя:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    reg_login_entry = tk.Entry(registration_window, font=("Arial", 10))
    reg_login_entry.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(registration_window, text="E-mail:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    reg_email_entry = tk.Entry(registration_window, font=("Arial", 10))
    reg_email_entry.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(registration_window, text="Пароль:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    reg_password_entry = tk.Entry(registration_window, font=("Arial", 10), show="*")
    reg_password_entry.pack(fill=tk.X, padx=5, pady=5)
    ToolTip(reg_password_entry, text="Пароль должен содержать:\n-Не менее 8 символов\n-Минимум 1 цифру\n-Cпец. символы: !,@,#,%,^,&,*,(,),~")
    tk.Label(registration_window, text="Повторите пароль:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(pady=10)
    reg_confirm_password_entry = tk.Entry(registration_window, font=("Arial", 10), show="*")
    reg_confirm_password_entry.pack(fill=tk.X, padx=5, pady=5)
    def handle_registration():
        global current_user
        username = reg_login_entry.get()
        address = reg_email_entry.get()
        password = reg_password_entry.get()
        confirm_password = reg_confirm_password_entry.get()
        if not username or not password or not confirm_password:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
            return
        def contains_digits(text):
            return any(char.isdigit() for char in text)
        def contains_special_chars(text):
            special_chars = set('!@#%^&*()~')
            return any(char in special_chars for char in text)
        def valid_email(email):
            return "@" in email and "." in email.split("@")[-1]
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM logins WHERE user_name = %s", (username,))
        user = cursor.fetchone()
        if user:
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
        elif password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают.")
        elif len(password) < 8:
            messagebox.showerror("Ошибка", "Пароль должен иметь не менее 8 символов.")
        elif not contains_digits(password):
            messagebox.showerror("Ошибка", "Пароль должен содержать минимум 1 цифру.")
        elif not contains_special_chars(password):
            messagebox.showerror("Ошибка", "Пароль должен содержать спец. символы: !,@,#,%,^,&,*,(,),~")
        elif not valid_email(address):
            messagebox.showerror("Ошибка", "Неверный формат электронной почты.")
        else:
            cursor.execute("INSERT INTO logins (user_name, email) VALUES (%s, %s) RETURNING login_id", (username, address))
            login_id = cursor.fetchone()[0]
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO passwords (login_id, password) VALUES (%s, %s)", (login_id, hashed_password))
            connection.commit()
            messagebox.showinfo("Регистрация", "Регистрация прошла успешно!")
            current_user = username
            root.title(f"{current_user} - Abayunda")
            for item in deck_list.get_children():
                deck_list.delete(item)
            cursor.close()
            connection.close()
            if current_user == "n" or current_user == "v":
                admin_menu = tk.Menu(menu_bar, tearoff=0)
                admin_menu.add_command(label="Режим админа", command=admin_mode)
                menu_bar.add_cascade(label="Админ", menu=admin_menu)
            registration_window.destroy()
    tk.Button(registration_window, text="Зарегистрироваться", font=("Arial", 10), bg="white", command=handle_registration).pack(pady=10)
    tk.Button(registration_window, text="Отмена", font=("Arial", 10), bg="white", command=lambda: (registration_window.destroy(), login())).pack(pady=5)

def create_deck():
    if current_user:
        deck_name_window = tk.Toplevel(root)
        deck_name_window.title("Abayunda")
        deck_name_window.geometry("400x115")
        deck_name_window.config(bg="#ffc83d")
        top_frame = tk.Frame(deck_name_window, bg="#ffc83d")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top_frame, text="Имя новой колоды:", font=("Arial", 10, "bold"), bg="#ffc83d").pack(anchor="w")
        deck_name_entry = tk.Entry(top_frame, font=("Arial", 10))
        deck_name_entry.pack(fill=tk.X, pady=5)
        button_frame = tk.Frame(deck_name_window, bg="#ffc83d")
        button_frame.pack(fill=tk.X, padx=10)
        def confirm_action():
            deck_name = deck_name_entry.get()
            if deck_name.strip():
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM decks WHERE deck_name = %s AND login_id = (SELECT login_id FROM logins WHERE user_name = %s)", (deck_name, current_user))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Ошибка", "Колода с таким названием уже существует!")
                    return
                cursor.execute("SELECT login_id FROM logins WHERE user_name = %s", (current_user,))
                user = cursor.fetchone()
                login_id = user[0]
                cursor.execute("INSERT INTO decks (deck_name, login_id) VALUES (%s, %s) RETURNING deck_id", (deck_name, login_id))
                deck_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO progress (deck_id, new_cards, learn_cards, repeat_cards) VALUES (%s, 0, 0, 0)", (deck_id,))
                connection.commit()
                cursor.close()
                connection.close()
                deck_list.insert("", "end", values=(deck_name, 0, 0, 0))
                deck_name_window.destroy()
        tk.Button(button_frame, text="Отмена", font=("Arial", 10), bg="white", command=deck_name_window.destroy, width=8).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="ОК", font=("Arial", 10), bg="white", command=confirm_action, width=5).pack(side=tk.RIGHT, padx=5)
    else:
        login()

def add_card():
    deck_choices = [deck_list.item(child)["values"][0] for child in deck_list.get_children()]
    if deck_choices:
        selected_deck = tk.StringVar(value=deck_choices[0])
        def select_deck(deck_listbox):
            selected_deck.set(deck_listbox.get(deck_listbox.curselection()))
        def choose_deck():
            nonlocal selected_deck
            choose_deck_window = tk.Toplevel(root)
            choose_deck_window.title("Выбрать колоду")
            choose_deck_window.geometry("400x250")
            choose_deck_window.config(bg="#ffc83d")
            deck_listbox = tk.Listbox(choose_deck_window, height=10, font=("Arial", 10))
            for deck in deck_choices:
                deck_listbox.insert(tk.END, deck)
            deck_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
            button_frame = tk.Frame(choose_deck_window, bg="#ffc83d")
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            tk.Button(button_frame, text="Отмена", font=("Arial", 10), bg="white", command=choose_deck_window.destroy, width=10).pack(side=tk.RIGHT, padx=5)
            tk.Button(button_frame, text="Добавить", font=("Arial", 10), bg="white", command=lambda:(create_deck(), choose_deck_window.destroy(), add_card_window.destroy()), width=10).pack(side=tk.RIGHT, padx=5)
            tk.Button(button_frame, text="Выбрать", font=("Arial", 10), bg="white", command=lambda:(select_deck(deck_listbox), choose_deck_window.destroy()), width=10).pack(side=tk.RIGHT, padx=5)
        add_card_window = tk.Toplevel(root)
        add_card_window.title("Добавить")
        add_card_window.geometry("500x250")
        add_card_window.config(bg="#ffc83d")
        top_frame = tk.Frame(add_card_window, bg="#ffc83d")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top_frame, text="Колода", font=("Arial", 10, "bold"), bg="#ffc83d").pack(side=tk.LEFT)
        tk.Button(top_frame, textvariable=selected_deck, font=("Arial", 10), bg="white", command=choose_deck).pack(fill=tk.X)
        card_frame = tk.Frame(add_card_window, bg="#ffc83d")
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(card_frame, text="Front", font=("Arial", 12, "bold"), bg="#ffc83d").pack(anchor="w")
        front_entry = tk.Entry(card_frame, font=("Arial", 18))
        front_entry.pack(fill=tk.X, padx=3, pady=5)
        tk.Label(card_frame, text="Back", font=("Arial", 12, "bold"), bg="#ffc83d").pack(anchor="w")
        back_entry = tk.Entry(card_frame, font=("Arial", 18))
        back_entry.pack(fill=tk.X, padx=3, pady=5)
        button_frame = tk.Frame(add_card_window, bg="#ffc83d")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        def save_card():
            deck = selected_deck.get()
            front = front_entry.get()
            back = back_entry.get()
            if front and back:
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM cards WHERE deck_id = (SELECT deck_id FROM decks WHERE deck_name = %s AND login_id = (SELECT login_id FROM logins WHERE user_name = %s)) AND front = %s AND back = %s", (deck, current_user, front, back))
                card_exists = cursor.fetchone()[0]
                if card_exists > 0:
                    messagebox.showerror("Ошибка", "Такая карточка уже существует!")
                else:
                    cursor.execute("SELECT deck_id FROM decks WHERE deck_name = %s AND login_id = (SELECT login_id FROM logins WHERE user_name = %s)", (deck, current_user))
                    deck_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO cards (deck_id, front, back, state) VALUES (%s, %s, %s, 'Новая')", (deck_id, front, back))
                    cursor.execute("UPDATE progress SET new_cards = new_cards + 1 WHERE deck_id = %s", (deck_id,))
                    connection.commit()
                    cursor.execute("""SELECT d.deck_name, p.new_cards, p.learn_cards, p.repeat_cards FROM decks d LEFT JOIN progress p ON d.deck_id = p.deck_id WHERE d.login_id = (SELECT login_id FROM logins WHERE user_name = %s)""", (current_user,))
                    decks = cursor.fetchall()
                    for item in deck_list.get_children():
                        deck_list.delete(item)
                    for deck in decks:
                        deck_name, new_cards, learn_cards, repeat_cards = deck
                        deck_list.insert("", "end", values=(deck_name, new_cards, learn_cards, repeat_cards))
                    connection.close()
                    front_entry.delete(0, tk.END)
                    back_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        tk.Button(button_frame, text="Закрыть", font=("Arial", 10), bg="white", width=10, command=add_card_window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Добавить", font=("Arial", 10), bg="white", width=10, command=save_card).pack(side=tk.RIGHT, padx=5)
    else:
        create_deck()

def prepare_to_learn(selected_item):
    selected_item = deck_list.selection()
    if not selected_item:
        return
    deck_data = deck_list.item(selected_item, "values")
    deck_name, new_count, learning_count, review_count = deck_data
    for widget in root.winfo_children():
        widget.pack_forget()
    top_frame.pack(side=tk.TOP, pady=20)
    tk.Label(root, text=deck_name, font=("Arial", 12, "bold"), bg="#ffc83d").pack(pady=10)
    content_frame = tk.Frame(root, bg="#ffc83d")
    content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    stats_frame = tk.Frame(content_frame, bg="#ffc83d")
    stats_frame.grid(row=0, column=0, padx=(150, 50), pady=20, sticky="w")
    tk.Label(stats_frame, text=f"Новые: {new_count}", font=("Arial", 12, "italic"), bg="#ffc83d").grid(row=0, column=0, pady=5)
    tk.Label(stats_frame, text=f"Изучаемые: {learning_count}", font=("Arial", 12, "italic"), bg="#ffc83d").grid(row=1, column=0, pady=5)
    tk.Label(stats_frame, text=f"К просмотру: {review_count}", font=("Arial", 12, "italic"), bg="#ffc83d").grid(row=2, column=0, pady=5)
    action_frame = tk.Frame(content_frame, bg="#ffc83d")
    action_frame.grid(row=0, column=1, padx=(50, 150), pady=20, sticky="e")
    btn_start_learn = tk.Button(action_frame, text="Учить", font=("Arial", 12), width=10, bg="white", command=learn_deck)
    btn_start_learn.grid(row=1, column=0, pady=5)
    ToolTip(btn_start_learn, text="Перейти к изучению")

def learn_deck():
    selected_item = deck_list.selection()
    if not selected_item:
        return
    deck_data = deck_list.item(selected_item, "values")
    deck_name, new_count, learning_count, review_count = deck_data
    new_count = int(new_count)
    learning_count = int(learning_count)
    review_count = int(review_count)
    for widget in root.winfo_children():
        widget.pack_forget()
    top_frame.pack(side=tk.TOP, pady=20)
    action_frame = tk.Frame(root, bg="#ffc83d")
    action_frame.pack(side=tk.BOTTOM, pady=20)
    tk.Label(root, text=deck_name, font=("Arial", 15, "bold"), bg="#ffc83d").pack(pady=10)
    content_frame = tk.Frame(root, bg="#ffc83d")
    content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("""SELECT card_id, front, back, state FROM cards WHERE deck_id = (SELECT deck_id FROM decks WHERE deck_name = %s)""", (deck_name,))
    cards = cursor.fetchall()
    cursor.close()
    connection.close()
    current_card = {"index": 0}
    def show_card():
        if current_card["index"] < len(cards):
            card_id, front, back, state = cards[current_card["index"]]
            front_label.config(text=front)
            back_label.config(text=back)
            back_label.pack_forget()
            btn_show_answer.pack()
        else:
            front_label.config(text="Ура! На сегодня всё.")
            back_label.pack_forget()
            btn_show_answer.pack_forget()
            hide_action_buttons()
    card_frame = tk.Frame(content_frame, width=300, height=150, relief=tk.RAISED, bd=2)
    card_frame.pack(side=tk.TOP, pady=20)
    front_label = tk.Label(card_frame, text="", font=("Arial", 18))
    front_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    back_label = tk.Label(card_frame, text="", font=("Arial", 18))
    def update_progress(response):
        nonlocal new_count, learning_count, review_count
        if current_card["index"] >= len(cards):
            return
        card_id, front, back, state = cards[current_card["index"]]
        new_state = state
        if state == "Новая":
            new_count -= 1
        elif state == "К просмотру":
            review_count -= 1
        elif state == "Изучаемая":
            learning_count -= 1
        if response == "Снова":
            new_state = "Изучаемая"
            learning_count += 1
            cards.append((card_id, front, back, new_state))
        elif response == "Трудно" or response == "Хорошо":
            new_state = "Изучаемая"
            learning_count += 1
        elif response == "Легко":
            new_state = "К просмотру"
            review_count += 1
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("""UPDATE cards SET state = %s WHERE card_id = %s""", (new_state, card_id))
        cursor.execute("""UPDATE progress SET new_cards = %s, learn_cards = %s, repeat_cards = %s WHERE deck_id = (SELECT deck_id FROM decks WHERE deck_name = %s)""", (new_count, learning_count, review_count, deck_name))
        connection.commit()
        cursor.close()
        connection.close()
        deck_list.item(selected_item, values=(deck_name, new_count, learning_count, review_count))
        current_card["index"] += 1
        hide_action_buttons()
        show_card()
    def show_action_buttons():
        btn_again.pack(side=tk.LEFT, padx=5)
        btn_hard.pack(side=tk.LEFT, padx=5)
        btn_good.pack(side=tk.LEFT, padx=5)
        btn_easy.pack(side=tk.LEFT, padx=5)
    def hide_action_buttons():
        btn_again.pack_forget()
        btn_hard.pack_forget()
        btn_good.pack_forget()
        btn_easy.pack_forget()
    def flip_card():
        flipping = {"value": False}
        def shrink():
            current_width = card_frame.winfo_width()
            if current_width > 10:
                new_width = current_width - 10
                card_frame.config(width=new_width)
                root.after(5, shrink)
                show_action_buttons()
            else:
                switch_text()
                expand()
        def expand():
            current_width = card_frame.winfo_width()
            if current_width < 300:
                new_width = current_width + 10
                card_frame.config(width=new_width)
                root.after(5, expand)
                show_action_buttons()
            else:
                card_frame.config(width=300)
                flipping["value"] = False
        def switch_text():
            if front_label.cget("text") == cards[current_card["index"]][1]:
                front_label.config(text=cards[current_card["index"]][2], fg="black")
            else:
                front_label.config(text=cards[current_card["index"]][1], fg="black")
        shrink()
    btn_show_answer = tk.Button(action_frame, text="Показать ответ", font=("Arial", 10), bg="white", command=lambda: [btn_show_answer.pack_forget(), flip_card()])
    btn_show_answer.pack()
    ToolTip(btn_show_answer, text="Узнайте правильный ответ и сравните со своим")
    btn_again = tk.Button(action_frame, text="Снова", font=("Arial", 10), bg="white", command=lambda: update_progress("Снова"))
    btn_hard = tk.Button(action_frame, text="Трудно", font=("Arial", 10), bg="white", command=lambda: update_progress("Трудно"))
    btn_good = tk.Button(action_frame, text="Хорошо", font=("Arial", 10), bg="white", command=lambda: update_progress("Хорошо"))
    btn_easy = tk.Button(action_frame, text="Легко", font=("Arial", 10), bg="white", command=lambda: update_progress("Легко"))
    show_card()

def return_to_decks():
    for widget in root.winfo_children():
        widget.pack_forget()
    top_frame.pack(side=tk.TOP, pady=20)
    deck_list.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
    bottom_frame.pack(side=tk.BOTTOM, pady=20)
    btn_create_deck.pack()

def deck_options(event, item):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Переименовать", command=lambda: rename_deck(item))
    menu.add_command(label="Удалить", command=lambda: delete_deck(item))
    menu.post(event.x_root, event.y_root)

def rename_deck(item):
    deck_name = deck_list.item(item, "values")[0]
    rename_window = tk.Toplevel(root)
    rename_window.title("Abayunda")
    rename_window.geometry("400x125")
    top_frame = tk.Frame(rename_window)
    top_frame.pack(fill=tk.X, padx=10, pady=10)
    tk.Label(top_frame, text="Имя новой колоды:", font=("Arial", 10)).pack(anchor="w")
    rename_entry = tk.Entry(top_frame, font=("Arial", 10))
    rename_entry.insert(0, deck_name)
    rename_entry.pack(fill=tk.X, pady=5)
    button_frame = tk.Frame(rename_window)
    button_frame.pack(fill=tk.X, padx=10)
    def confirm_rename():
        new_name = rename_entry.get()
        if new_name.strip():
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM decks WHERE deck_name = %s AND login_id = (SELECT login_id FROM logins WHERE user_name = %s)", (new_name, current_user))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Колода с таким названием уже существует!")
                return
            cursor.execute("SELECT deck_id FROM decks WHERE deck_name = %s", (deck_name,))
            deck_id = cursor.fetchone()
            cursor.execute("UPDATE decks SET deck_name = %s WHERE deck_id = %s", (new_name, deck_id))
            connection.commit()
            connection.close()
            deck_list.item(item, values=(new_name, *deck_list.item(item)["values"][1:]))
            rename_window.destroy()
    tk.Button(button_frame, text="Отмена", font=("Arial", 10), command=rename_window.destroy, width=8).pack(side=tk.RIGHT, padx=5)
    tk.Button(button_frame, text="ОК", font=("Arial", 10), command=confirm_rename, width=5).pack(side=tk.RIGHT, padx=5)

def delete_deck(item):
    deck_name = deck_list.item(item, "values")[0]
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT deck_id FROM decks WHERE deck_name = %s", (deck_name,))
    deck_id = cursor.fetchone()
    cursor.execute("DELETE FROM cards WHERE deck_id = %s", (deck_id,))
    cursor.execute("DELETE FROM progress WHERE deck_id = %s", (deck_id,))
    cursor.execute("DELETE FROM decks WHERE deck_id = %s", (deck_id,))
    connection.commit()
    connection.close()
    deck_list.delete(item)
    messagebox.showinfo("Удаление", f"Колода {deck_name} удалена.")

def admin_mode():
    admin_window = tk.Toplevel(root)
    admin_window.title("Режим администратора")
    admin_window.geometry("400x450")
    admin_window.config(bg="#ffc83d")
    def show_user_deck_info():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("""CREATE VIEW users_info AS SELECT logins.user_name, decks.deck_name, COUNT(cards.card_id) AS total_cards FROM decks RIGHT JOIN logins ON decks.login_id = logins.login_id LEFT JOIN cards ON decks.deck_id = cards.deck_id GROUP BY logins.user_name, decks.deck_name;""")
            cursor.execute("""SELECT * FROM users_info;""")
            result_window = tk.Toplevel(root)
            result_window.title("Информация о колодах и пользователях")
            result_window.geometry("700x400")
            admin_window.config(bg="#ffc83d")
            treeview = ttk.Treeview(result_window, columns=("User", "Deck", "Total Cards"), show="headings", height=15)
            treeview.pack(fill="both", expand=True, padx=20, pady=20)
            treeview.heading("User", text="Пользователь")
            treeview.heading("Deck", text="Колода")
            treeview.heading("Total Cards", text="Общее количество карточек")
            treeview.column("User", width=150, anchor="center")
            treeview.column("Deck", width=200, anchor="center")
            treeview.column("Total Cards", width=150, anchor="center")
            rows = cursor.fetchall()
            for row in rows:
                treeview.insert("", "end", values=row)
            cursor.execute("""DROP VIEW users_info;""")
            cursor.close()
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
    def delete_all_tables():
        response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все таблицы?")
        if response:
            try:
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("""DROP TABLE progress;""")
                cursor.execute("""DROP TABLE cards;""")
                cursor.execute("""DROP TABLE decks;""")
                cursor.execute("""DROP TABLE passwords;""")
                cursor.execute("""DROP TABLE logins;""")
                connection.commit()
                cursor.close()
                connection.close()
                messagebox.showinfo("Успешно", "Все таблицы удалены. Запустите программу заново для продолжения работы")
                root.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить все таблицы: {e}")
    def clear_all_tables():
        response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить все таблицы?")
        if response:
            try:
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("""TRUNCATE TABLE progress CASCADE;""")
                cursor.execute("""TRUNCATE TABLE cards CASCADE;""")
                cursor.execute("""TRUNCATE TABLE decks CASCADE;""")
                cursor.execute("""TRUNCATE TABLE passwords CASCADE;""")
                cursor.execute("""TRUNCATE TABLE logins CASCADE;""")
                connection.commit()
                cursor.close()
                connection.close()
                messagebox.showinfo("Успешно", "Все таблицы очищены. Запустите программу заново для продолжения работы")
                root.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить все таблицы: {e}")
    def add_column():
        table = table_combobox.get()
        column_name = column_name_entry.get()
        data_type = data_type_combobox.get()
        if not table or not column_name or not data_type:
            messagebox.showwarning("Ошибка", "Заполните все поля перед добавлением колонки.")
            return
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {data_type};")
            connection.commit()
            cursor.close()
            connection.close()
            messagebox.showinfo("Успешно", f"Колонка '{column_name}' ({data_type}) добавлена в таблицу '{table}'.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить колонку: {e}")
        messagebox.showinfo("Успешно", f"Колонка '{column_name}' ({data_type}) добавлена в таблицу '{table}'.")
    btn_show_info = tk.Button(admin_window, text="Показать данные о пользователях", font=("Arial", 12), bg="white", command=show_user_deck_info, width=30)
    btn_show_info.pack(pady=10)
    btn_delete_tables = tk.Button(admin_window, text="Удалить все таблицы", font=("Arial", 12), bg="white", command=delete_all_tables, width=30)
    btn_delete_tables.pack(pady=10)
    btn_clear_tables = tk.Button(admin_window, text="Очистить все таблицы", font=("Arial", 12), bg="white", command=clear_all_tables, width=30)
    btn_clear_tables.pack(pady=10)
    tk.Label(admin_window, text="Добавить колонку", font=("Arial", 12, "bold"), bg="#ffc83d").pack(pady=10)
    tk.Label(admin_window, text="Выберите таблицу:", font=("Arial", 12, "bold"), bg="#ffc83d").pack(anchor="w", padx=20)
    table_combobox = ttk.Combobox(admin_window, values=["logins", "passwords", "decks", "cards", "progress"], state="readonly")
    table_combobox.pack(fill="x", padx=20, pady=5)
    tk.Label(admin_window, text="Название колонки:", font=("Arial", 12, "bold"), bg="#ffc83d").pack(anchor="w", padx=20)
    column_name_entry = tk.Entry(admin_window)
    column_name_entry.pack(fill="x", padx=20, pady=5)
    tk.Label(admin_window, text="Тип данных:", font=("Arial", 12, "bold"), bg="#ffc83d").pack(anchor="w", padx=20)
    data_type_combobox = ttk.Combobox(admin_window, values=["TEXT", "INTEGER"], state="readonly")
    data_type_combobox.pack(fill="x", padx=20, pady=5)
    btn_add_column = tk.Button(admin_window, text="Добавить колонку", font=("Arial", 12), bg="white", command=add_column, width=30)
    btn_add_column.pack(pady=10)

connection = connect_to_db()
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS logins (login_id SERIAL PRIMARY KEY, user_name VARCHAR(255) UNIQUE, email VARCHAR(255) UNIQUE);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS passwords (password_id SERIAL PRIMARY KEY, login_id INT REFERENCES logins(login_id) ON DELETE CASCADE, password VARCHAR(255));""")
cursor.execute("""CREATE TABLE IF NOT EXISTS decks (deck_id SERIAL PRIMARY KEY, deck_name VARCHAR(255), login_id INT REFERENCES logins(login_id) ON DELETE CASCADE);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS cards (card_id SERIAL PRIMARY KEY, deck_id INT REFERENCES decks(deck_id) ON DELETE CASCADE, front VARCHAR(255), back VARCHAR(255), state VARCHAR(50));""")
cursor.execute("""CREATE TABLE IF NOT EXISTS progress (progress_id SERIAL PRIMARY KEY, deck_id INT REFERENCES decks(deck_id) ON DELETE CASCADE, new_cards INT, learn_cards INT, repeat_cards INT);""")
connection.commit()
cursor.close()
connection.close()

current_user = None

root = tk.Tk()
root.title("Abayunda")
root.geometry("650x550")
root.config(bg="#ffc83d")

top_frame = tk.Frame(root, bg="#ffc83d")
top_frame.pack(side=tk.TOP, pady=20)
btn_return_to_decks = tk.Button(top_frame, text="Колоды", font=("Arial", 12, "bold"), width=10, command=return_to_decks, bg="white")
btn_return_to_decks.pack(side=tk.LEFT, padx=10)
ToolTip(btn_return_to_decks, text="Вернуться к списку колод")
btn_add_card = tk.Button(top_frame, text="Добавить", font=("Arial", 12, "bold"), width=10, command=add_card, bg="white")
btn_add_card.pack(side=tk.LEFT, padx=10)
ToolTip(btn_add_card, text="Чтобы добавить карточку, нужно выбрать колоду и написать front/back")

style = ttk.Style()
style.configure("Treeview", font=("Arial", 12), rowheight=20)
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
columns = ("deck_name", "new", "learning", "to_review")
deck_list = ttk.Treeview(root, columns=columns, show="headings", height=10)
deck_list.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
deck_list.heading("deck_name", text="Колода")
deck_list.heading("new", text="Новые")
deck_list.heading("learning", text="Изучаемые")
deck_list.heading("to_review", text="К просмотру")
deck_list.column("deck_name", width=200, anchor="center")
deck_list.column("new", width=100, anchor="center")
deck_list.column("learning", width=100, anchor="center")
deck_list.column("to_review", width=100, anchor="center")

bottom_frame = tk.Frame(root, bg="#ffc83d")
bottom_frame.pack(side=tk.BOTTOM, pady=20)
btn_create_deck = tk.Button(bottom_frame, text="Создать колоду", font=("Arial", 10, "bold"), width=15, command=create_deck, bg="white")
btn_create_deck.pack()
ToolTip(btn_create_deck, text="Без колод вы не сможете создавать карточки")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Сменить профиль\t (Ctrl+Shift+P)", command=login)
file_menu.add_separator()
file_menu.add_command(label="Выход\t (Ctrl+Q)", command=root.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)
about_menu = tk.Menu(menu_bar, tearoff=0)
about_menu.add_command(label="О программе...\t (F1)", command=info)
menu_bar.add_cascade(label="Справка", menu=about_menu)
root.config(menu=menu_bar)

deck_list.bind("<Double-1>", prepare_to_learn)
deck_list.bind("<Button-3>", lambda event: deck_options(event, deck_list.identify_row(event.y)))

root.bind("<Control-Shift-P>", login)
root.bind("<Control-q>", lambda event=None: root.quit())
root.bind("<F1>", info)

root.mainloop()