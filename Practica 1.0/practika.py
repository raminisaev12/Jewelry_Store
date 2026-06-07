import tkinter as tk
from re import search
from tkinter import ttk
from PIL import Image, ImageTk
import mysql.connector
from tkinter import messagebox
import random
import string



root = tk.Tk()
root.title("Алмазный путь")
root.geometry("600x400")
root.state('zoomed')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)


bg_color = "#FDF5E6"
text_color = "#2D6A4F"
root.configure(bg=bg_color)
root.rowconfigure(1, weight=1)

img = Image.open("logo.png")
img = img.resize((40, 40))
logo_img = ImageTk.PhotoImage(img)

# Логотип
frame = tk.Frame(root,bg=bg_color)
frame.grid(column=0, row=0, sticky="ew")

label_logo = tk.Label(frame, image=logo_img, bg=bg_color)
label_logo.grid(row=0, column=0, padx=(20, 5), pady=20, sticky="w")

# Заголовок
label_zagol = tk.Label(frame, text="Алмазный путь",
                       fg=text_color,
                       font=("Segoe UI", 22, "bold"),
                       bg=bg_color)
label_zagol.grid(row=0, column=0, padx=65, pady=20, sticky="w")

border_frame = tk.Frame(frame, bg=bg_color, highlightbackground="black",highlightcolor="black", highlightthickness=1)
border_frame.grid(row=1, column=0, padx=20, pady=2, sticky="w")

dobavl = tk.Label(border_frame, text="Добавление изделия", fg="#4A7C59",
                  font=("Segoe UI", 12, "italic"), bg=bg_color)
dobavl.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

##добавление
for i in range(6):
    border_frame.columnconfigure(i * 2, weight=0)  # Для Label
    border_frame.columnconfigure(i * 2 + 1, weight=1)  # Для Entry

def create_field(label_text, col_idx):
    lbl = tk.Label(border_frame, text=label_text, bg=bg_color, fg=text_color)
    lbl.grid(row=1, column=col_idx * 2, padx=(10, 5), pady=10, sticky="ew")

    ent = tk.Entry(border_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#A0A0A0")
    ent.grid(row=1, column=col_idx * 2 + 1, padx=(0, 10), pady=10, sticky="ew")
    return ent
####
def create_combobox(label_text, col_idx, values_list):
    lbl = tk.Label(border_frame, text=label_text, bg=bg_color, fg=text_color)
    lbl.grid(row=1, column=col_idx * 2, padx=(10, 5), pady=10, sticky="ew")

    combobox = ttk.Combobox(border_frame, values=values_list, state="readonly")
    combobox.grid(row=1, column=col_idx * 2 + 1, padx=(0, 10), pady=10, sticky="ew")

    return combobox

# Создаем поля по порядку
Entry_name = create_field("Название изделия", 0)
Entry_type = create_combobox("Тип", 1, ["Кольцо", "Серьги", "Браслет", "Цепочка"])
Entry_category = create_combobox("Категория", 2, ["Свадебные", "Женские", "Мужские","Детские"])
Entry_metal = create_combobox("Металл", 3,["Золото","Красное золото","Белое золото","Желтое золото","Серебро"])
Entry_gemstone = create_combobox("Камень", 4, ["Нет", "Бриллиант", "Сапфир", "Рубин", "Изумруд", "Фианит"])
Entry_purity = create_field("Проба", 5)
Entry_weight = create_field("Вес (г)", 6)
Entry_price = create_field("Цена (₽)", 7)

####скелет
cols = ('id', 'name', 'type', 'category', 'metal', 'gemstone', 'purity', 'weight', 'price')

tree = ttk.Treeview(root, columns=cols, show='headings',height=12)

tree.heading('id', text='ID',anchor="center")
tree.heading('name', text='Название изделия',anchor="center")
tree.heading('category', text='Категория',anchor="center")
tree.heading('type', text='Тип',anchor="center")
tree.heading('metal', text='Металл',anchor="center")
tree.heading('gemstone', text='Камень',anchor="center")
tree.heading('purity', text='Проба',anchor="center")
tree.heading('weight', text='Вес (г)',anchor="center")
tree.heading('price', text='Цена (₽)',anchor="center")

for col in cols:
    tree.column(col,width=100,anchor="center")

tree.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")



#меню
Menu = tk.Menu(root)
root.config(menu=Menu)

filter_menu = tk.Menu(Menu, tearoff=0,fg=text_color)
Menu.add_cascade(label="Фильтры", menu=filter_menu)

filter_menu2 = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="Название изделия", menu=filter_menu2)


sort_menu = tk.Menu(Menu, tearoff=0)
Menu.add_cascade(label="Сортировки", menu=sort_menu)
sort_menu.add_command(label="Сортировка от А до Я")
sort_menu.add_command(label="Сортировка от Я до А")
sort_menu.add_command(label="Сначала дешевые")


###базза данных
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="diamond_path"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT @@hostname, @@port;")
        host_info = cursor.fetchone()
        print(f"DEBUG: Подключились к серверу: {host_info[0]}, порт: {host_info[1]}")
        cursor.close()

        return connection
    except mysql.connector.Error as err:
        print(f"Ошибка подключения: {err}")
        return None

def load_data_from_db():
    for item in tree.get_children():
        tree.delete(item)

    conn = None
    try:
        conn = connect_to_db()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT CONCAT(prefix, '-', id), name, type, category, metal, gemstone, purity, weight, price FROM jewelry_items")
            rows = cursor.fetchall()
            print(f"Найдено записей в базе: {len(rows)}") # ЭТО ПОКАЖЕТ, ЧТО ПРИШЛО ИЗ БАЗЫ

            for row in rows:
                tree.insert("", tk.END, values=row)

            cursor.close()
        else:
            print("Соединение с базой не удалось!")
    except mysql.connector.Error as err:
        print(f"Ошибка при работе с данными: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()
load_data_from_db()

def generate_five_digit_id():
    return random.randint(10000, 99999)

def add_item_to_db():
    # Собираем данные
    new_id = generate_five_digit_id()
    data = {
        "Название": Entry_name.get(),
        "Тип": Entry_type.get(),
        "Категория": Entry_category.get(),
        "Металл": Entry_metal.get(),
        "Камень": Entry_gemstone.get(),
        "Проба": Entry_purity.get(),
        "Вес": Entry_weight.get(),
        "Цена": Entry_price.get()
    }

    # Проверка на пустоту
    for label, value in data.items():
        if not value.strip():
            messagebox.showwarning("Ошибка", f"Поле '{label}' обязательно!")
            return

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # SQL запрос
        cursor.execute("CALL AddJewelry(%s, %s, %s, %s, %s, %s, %s, %s)", (
            data["Название"],
            data["Тип"],
            data["Категория"],
            data["Металл"],
            data["Проба"],  # 5-й параметр
            data["Вес"],  # 6-й параметр
            data["Цена"],  # 7-й параметр
            data["Камень"]  # 8-й параметр (он теперь последний!)
        ))

        conn.commit()
        print(f"Успешно добавлено строк: {cursor.rowcount}")

        cursor.close()

        # Очистка
        Entry_name.delete(0, tk.END)
        Entry_type.set("")
        Entry_category.set("")
        Entry_metal.set("")
        Entry_gemstone.set("")
        Entry_purity.delete(0, tk.END)
        Entry_weight.delete(0, tk.END)
        Entry_price.delete(0, tk.END)

        messagebox.showinfo("Успех", "Изделие добавлено!")
        load_data_from_db()


    except Exception as e:

        messagebox.showerror("Ошибка", f"Не удалось добавить в базу:\n{e}")

    finally:

        if conn:
            conn.close()


# Сама кнопка
btn_add = tk.Button(border_frame, text="Добавить изделие", command=add_item_to_db, bg="#2D6A4F", fg="white")
btn_add.grid(row=2, column=0, columnspan=12, pady=10)

###выборка
def search_data(event=None):
    search = viborka.get()


    for item in tree.get_children():
        tree.delete(item)


    conn = connect_to_db()
    try:
        if conn and conn.is_connected():
            cursor = conn.cursor()
            query = """
                SELECT CONCAT(prefix, '-', id), name, type, category, metal, gemstone, purity, weight, price 
                FROM jewelry_items 
                WHERE name LIKE %s
            """
            search_pattern = f"%{search}%"
            cursor.execute(query, (search_pattern,))

            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
            cursor.close()

    except mysql.connector.Error as err:
        print(f"Ошибка поиска: {err}")

    finally:
            if conn and conn.is_connected():
                conn.close()


viborka_label=tk.Label(root,text="Поиск изделия",fg=text_color,bg=bg_color,font=("Segoe UI", 12, "italic"))
viborka_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")


viborka = ttk.Entry(root,width=30)
viborka.grid(row=1, column=0, padx=125, pady=5, sticky="w")

viborka.bind("<KeyRelease>",search_data)


root.mainloop()