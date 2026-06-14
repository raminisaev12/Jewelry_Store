import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import mysql.connector
from tkinter import messagebox
import random



root = tk.Tk()
root.title("Алмазный путь")
root.geometry("600x400")
root.state('zoomed')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

l =Image.open("logo2.png")
l  = ImageTk.PhotoImage(l)

root.iconphoto(True, l)

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

####
def create_field(label_text, row_idx, col_idx):
    lbl = tk.Label(border_frame, text=label_text, bg=bg_color, fg=text_color)
    # Используем row_idx вместо жесткой единицы
    lbl.grid(row=row_idx, column=col_idx * 2, padx=(10, 5), pady=10, sticky="ew")

    ent = tk.Entry(border_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#A0A0A0")
    ent.grid(row=row_idx, column=col_idx * 2 + 1, padx=(0, 10), pady=10, sticky="ew")
    return ent

def create_combobox(label_text, row_idx, col_idx, values_list):
    lbl = tk.Label(border_frame, text=label_text, bg=bg_color, fg=text_color)
    # Используем row_idx вместо жесткой единицы
    lbl.grid(row=row_idx, column=col_idx * 2, padx=(10, 5), pady=10, sticky="ew")

    combobox = ttk.Combobox(border_frame, values=values_list, state="readonly")
    combobox.grid(row=row_idx, column=col_idx * 2 + 1, padx=(0, 10), pady=10, sticky="ew")
    return combobox

# Создаем поля по порядку
Entry_name = create_field("Название изделия", 1, 0)
Entry_type = create_combobox("Тип", 1, 1, ["Кольцо", "Серьги", "Браслет", "Цепочка"])
Entry_category = create_combobox("Категория", 1, 2, ["Свадебные", "Женские", "Мужские", "Детские"])
Entry_metal = create_combobox("Металл", 1, 3, ["Золото", "Красное золото", "Белое золото", "Желтое золото", "Серебро"])
Entry_gemstone = create_combobox("Камень", 1, 4, ["Нет", "Бриллиант", "Сапфир", "Рубин", "Изумруд", "Фианит"])

Entry_purity = create_field("Проба", 2, 0)
Entry_weight = create_field("Вес (г)", 2, 1)
Entry_price = create_field("Цена (₽)", 2, 2)
Entry_size = create_combobox("Размер", 2, 3, ["15", "15.5", "16", "16.5", "17", "17.5", "18"])
Entry_quantity = create_field("Количество", 2, 4)

lbl_size = tk.Label(border_frame, text="Размер", bg=bg_color, fg=text_color)
lbl_size.grid(row=2, column=3 * 2, padx=(10, 5), pady=10, sticky="ew")

Entry_size = ttk.Combobox(border_frame, values=["15", "16", "17", "18"], state="readonly")
Entry_size.grid(row=2, column=3 * 2 + 1, padx=(0, 10), pady=10, sticky="ew")
# Функция для обновления списка размеров в зависимости от типа
def update_size_options(event):
    selected_type = Entry_type.get()

    if selected_type == "Серьги":
        lbl_size.config(text="Размер")  # Для серег можно просто скрыть или оставить "Размер"
        Entry_size['values'] = ["—"]
        Entry_size.set("—")

    elif selected_type == "Кольцо":
        lbl_size.config(text="Размер")
        Entry_size['values'] = ["15", "15.5", "16", "16.5", "17", "17.5", "18", "18.5", "19"]
        Entry_size.set("17")

    elif selected_type == "Браслет":
        lbl_size.config(text="Обхват (см)")
        Entry_size['values'] = ["16", "17", "18", "19", "20", "21"]
        Entry_size.set("18")

    elif selected_type == "Цепочка":
        lbl_size.config(text="Длина (см)")
        Entry_size['values'] = ["40", "45", "50", "55", "60", "65"]
        Entry_size.set("45")

    else:
        lbl_size.config(text="Размер")
        Entry_size['values'] = ["—"]
        Entry_size.set("—")

Entry_type.bind("<<ComboboxSelected>>", update_size_options)
####скелет
cols = ('id', 'name', 'type', 'category', 'metal', 'gemstone', 'purity', 'weight', 'size', 'quantity', 'price')

tree = ttk.Treeview(root, columns=cols, show='headings',height=12)

tree.heading('id', text='ID',anchor="center")
tree.heading('name', text='Название изделия',anchor="center")
tree.heading('category', text='Категория',anchor="center")
tree.heading('type', text='Тип',anchor="center")
tree.heading('metal', text='Металл',anchor="center")
tree.heading('gemstone', text='Камень',anchor="center")
tree.heading('purity', text='Проба',anchor="center")
tree.heading('weight', text='Вес (г)',anchor="center")
tree.heading('size',text='Размер', anchor="center")
tree.heading('quantity', text='Кол-во', anchor="center")
tree.heading('price', text='Цена (₽)',anchor="center")
for col in cols:
    tree.column(col,width=100,anchor="center")

tree.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")

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
            cursor.execute("""
                            SELECT CONCAT(prefix, '-', id), name, type, category, metal, gemstone, purity, weight, size, quantity, price 
                            FROM jewelry_items
                        """)
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

def delete_selected_item():
    selected_item = tree.selection()

    if not selected_item:
        messagebox.showwarning("Внимание","Выберите изделия для удаления")
        return
    if not messagebox.askyesno("Удаление","Вы уверены, что хотите удалить изделие"):
        return

    item_data = tree.item(selected_item, "values")
    full_id = item_data[0]

    try:
        numeric_id = full_id.split("-")[1]
    except IndexError:
        messagebox.showerror("Ошибка","Не удалось определить ID изделия")
        return

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jewelry_items WHERE id = %s", (numeric_id,))
        conn.commit()
        cursor.close()
        messagebox.showinfo("Успех", "Изделие успешно удалено!")
        update_filters()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить из базы:\n{e}")

    finally:
        if conn and conn.is_connected():
            conn.close()


def reset_sorting():
    global current_sort_clause
    current_sort_clause = ""
    # Обновляем либо через фильтры (если они активны), либо просто грузим базу
    if any([var_ring.get(), var_earrings.get(), var_bracelet.get(), var_chain.get(),
            var_wedding.get(), var_woman.get(), var_man.get(), var_childish.get(),
            var_gold.get(), var_redgold.get(), var_whitegold.get(), var_yellowgold.get(), var_serebro.get(),
            var_no.get(), var_diamond.get(), var_sapphire.get(), var_ruby.get(), var_emerald.get(), var_cubic_zirconia.get()]):
        update_filters()
    else:
        load_data_from_db()

def reset_filters():
    viborka.delete(0, tk.END)
    for var in [var_ring, var_earrings, var_bracelet, var_chain, var_wedding, var_woman,
               var_man, var_childish, var_gold, var_redgold, var_whitegold, var_yellowgold,
               var_serebro, var_no, var_diamond, var_sapphire, var_ruby, var_emerald, var_cubic_zirconia]:
        var.set(False)
    # Если сортировка была, нужно ее сохранить при обновлении, поэтому вызываем update_filters
    update_filters()

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
        "Размер": Entry_size.get(),
        "Количество": Entry_quantity.get(),
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
        cursor.execute("CALL AddJewelry(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
            Entry_name.get(),
            Entry_type.get(),
            Entry_category.get(),
            Entry_metal.get(),
            Entry_purity.get(),
            Entry_weight.get(),
            Entry_quantity.get(),  # Количество
            Entry_price.get(),  # Цена
            Entry_gemstone.get(),
            Entry_size.get()
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
btn_add.grid(row=3, column=0, columnspan=12, pady=20)

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
                SELECT CONCAT(prefix, '-', id), name, type, category, metal, gemstone, purity, weight, size, quantity, price 
                FROM jewelry_items
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

# Текущее правило сортировки (пусто по умолчанию)
current_sort_clause = ""


def open_buy_window():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Внимание", "Выберите изделие для покупки")
        return

    item_data = tree.item(selected_item, "values")
    item_name = item_data[1]
    price_per_item = float(item_data[10])
    available_qty = int(item_data[9])

    buy_win = tk.Toplevel(root)
    buy_win.title(f"Покупка: {item_name}")
    buy_win.geometry("350x520")
    buy_win.configure(bg=bg_color)

    tk.Label(buy_win, text=f"Изделие: {item_name}", font=("Segoe UI", 12, "bold"), bg=bg_color, fg=text_color).pack(
        pady=10)

    # Продавец
    tk.Label(buy_win, text="Продавец ФИО:", bg=bg_color, fg=text_color).pack()
    combo_seller = ttk.Combobox(buy_win, values=["Иванов И.И.", "Петров П.П.", "Сидорова А.А."], state="readonly")
    combo_seller.pack(pady=5)
    combo_seller.current(0)

    # Количество
    tk.Label(buy_win, text="Количество:", bg=bg_color, fg=text_color).pack()
    koli = tk.Entry(buy_win, width=10, justify="center")
    koli.insert(0, "1")
    koli.pack(pady=5)

    # Способ оплаты
    payment_frame = tk.LabelFrame(buy_win, text="Способ оплаты", bg=bg_color, fg=text_color, padx=10, pady=10)
    payment_frame.pack(pady=15, padx=30, fill="x")
    payment_method = tk.StringVar(value="Наличные")

    for opt in ["Наличные", "Карта", "Перевод"]:
        tk.Radiobutton(payment_frame, text=opt, variable=payment_method, value=opt, bg=bg_color,
                       selectcolor=bg_color).pack(anchor="w")

    # Метка для итоговой суммы
    total_label = tk.Label(buy_win, text=f"К оплате: {price_per_item} ₽", font=("Segoe UI", 12, "bold"),bg=bg_color, fg="#C1121F")
    total_label.pack(pady=10)

    #Функция расчета
    def calculate_total(*args):
        qty_str = koli.get()
        if qty_str.isdigit():
            total = int(qty_str) * price_per_item
            total_label.config(text=f"К оплате: {total:,.2f} ₽")
        else:
            total_label.config(text="К оплате: ошибка")

    koli.bind("<KeyRelease>", calculate_total)

    def confirm_purchase():
        qty_str = koli.get()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showwarning("Ошибка", "Введите корректное количество!")
            return

        qty = int(qty_str)
        if qty > available_qty:
            messagebox.showwarning("Мало товара", f"В наличии только {available_qty} шт.")
            return

        try:
            numeric_id = item_data[0].split("-")[1]
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE jewelry_items SET quantity = quantity - %s WHERE id = %s", (qty, numeric_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех",
                                f"Покупка оформлена!\nПродавец: {combo_seller.get()}\nОплата: {payment_method.get()}")
            buy_win.destroy()
            load_data_from_db()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить БД: {e}")

    tk.Button(buy_win, text="Подтвердить", command=confirm_purchase, bg=text_color, fg="white", width=20).pack(pady=10)


def set_sort(sort_clause):
    global current_sort_clause
    #Запоминаем выбор пользователя (например, "price ASC" или "name DESC")
    current_sort_clause = sort_clause
    update_filters()

##по типу
var_ring = tk.BooleanVar()
var_earrings = tk.BooleanVar()
var_bracelet = tk.BooleanVar()
var_chain = tk.BooleanVar()

#по категории
var_wedding = tk.BooleanVar()
var_woman= tk.BooleanVar()
var_man= tk.BooleanVar()
var_childish= tk.BooleanVar()

#по металлу
var_gold= tk.BooleanVar()
var_redgold= tk.BooleanVar()
var_whitegold= tk.BooleanVar()
var_yellowgold= tk.BooleanVar()
var_serebro= tk.BooleanVar()

#по камням
var_no= tk.BooleanVar()
var_diamond= tk.BooleanVar()
var_sapphire= tk.BooleanVar()
var_ruby= tk.BooleanVar()
var_emerald= tk.BooleanVar()
var_cubic_zirconia= tk.BooleanVar()

def update_filters():
    # 1. Собираем списки выбора
    selected_types = []
    if var_ring.get(): selected_types.append("Кольцо")
    if var_earrings.get(): selected_types.append("Серьги")
    if var_bracelet.get(): selected_types.append("Браслет")
    if var_chain.get(): selected_types.append("Цепочка")

    selected_categories = []
    if var_wedding.get(): selected_categories.append("Свадебные")
    if var_woman.get(): selected_categories.append("Женские")
    if var_man.get(): selected_categories.append("Мужские")
    if var_childish.get(): selected_categories.append("Детские")

    selected_metal = []
    if var_gold.get(): selected_metal.append("Золото")
    if var_redgold.get(): selected_metal.append("Красное золото")
    if var_whitegold.get(): selected_metal.append("Белое золото")
    if var_yellowgold.get(): selected_metal.append("Желтое золото")
    if var_serebro.get(): selected_metal.append("Серебро")

    selected_gemstone = []
    if var_no.get(): selected_gemstone.append("Нет")
    if var_diamond.get(): selected_gemstone.append("Бриллиант")
    if var_sapphire.get(): selected_gemstone.append("Сапфир")
    if var_ruby.get(): selected_gemstone.append("Рубин")
    if var_emerald.get(): selected_gemstone.append("Изумруд")
    if var_cubic_zirconia .get(): selected_gemstone.append("Фианит")

    # 2. Формируем запрос
    query = """
    SELECT CONCAT(prefix, '-', id), name, type, category, metal, gemstone, purity, weight, size, quantity, price 
    FROM jewelry_items 
    WHERE 1=1
"""
    params = []

    if selected_types:
        placeholders = ', '.join(['%s'] * len(selected_types))
        query += f" AND type IN ({placeholders})"
        params.extend(selected_types)

    if selected_categories:
        placeholders = ', '.join(['%s'] * len(selected_categories))
        query += f" AND category IN ({placeholders})"
        params.extend(selected_categories)

    if selected_metal:
        placeholders = ', '.join(['%s'] * len(selected_metal))
        query += f" AND metal IN ({placeholders})"
        params.extend(selected_metal)

    if selected_gemstone:
        placeholders = ', '.join(['%s'] * len(selected_gemstone))
        query += f" AND gemstone IN ({placeholders})"
        params.extend(selected_gemstone)

    #ДОБАВЛЯЕМ СОРТИРОВКУ
    if current_sort_clause:
        query += f" ORDER BY {current_sort_clause}"

    # 3. Выполняем
    conn = None
    try:
        conn = connect_to_db()
        if conn and conn.is_connected():
            cursor = conn.cursor()

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            # Очищаем и обновляем
            for item in tree.get_children():
                tree.delete(item)
            for row in rows:
                tree.insert("", tk.END, values=row)
            cursor.close()
    except mysql.connector.Error as err:
        print(f"Ошибка фильтрации: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()

#меню
#фильтры
Menu = tk.Menu(root)
root.config(menu=Menu)

filter_menu = tk.Menu(Menu, tearoff=0,fg=text_color)
Menu.add_cascade(label="Фильтры", menu=filter_menu)

filter_menu2 = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="Название изделия", menu=filter_menu2)

#по типу
type_menu = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="По типу", menu=type_menu)

type_menu.add_checkbutton(label="Кольцо", variable=var_ring, command=update_filters)
type_menu.add_checkbutton(label="Серьги", variable=var_earrings, command=update_filters)
type_menu.add_checkbutton(label="Браслет", variable=var_bracelet, command=update_filters)
type_menu.add_checkbutton(label="Цепочка", variable=var_chain, command=update_filters)

#категория
cat_menu = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="По категории", menu=cat_menu)

cat_menu.add_checkbutton(label="Свадебные", variable=var_wedding, command=update_filters)
cat_menu.add_checkbutton(label="Женские", variable=var_woman, command=update_filters)
cat_menu.add_checkbutton(label="Мужские", variable=var_man, command=update_filters)
cat_menu.add_checkbutton(label="Детские", variable=var_childish, command=update_filters)

#по металлу
metal_menu = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="По металлу", menu=metal_menu)

metal_menu.add_checkbutton(label="Золото", variable=var_gold, command=update_filters)
metal_menu.add_checkbutton(label="Красное золото", variable=var_redgold, command=update_filters)
metal_menu.add_checkbutton(label="Белое золото", variable=var_whitegold, command=update_filters)
metal_menu.add_checkbutton(label="Желтое золото", variable=var_yellowgold, command=update_filters)
metal_menu.add_checkbutton(label="Серебро", variable=var_serebro, command=update_filters)
#по камню
stone_menu = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="По камню", menu=stone_menu)

stone_menu.add_checkbutton(label="Нет", variable=var_no, command=update_filters)
stone_menu.add_checkbutton(label="Бриллиант", variable=var_diamond, command=update_filters)
stone_menu.add_checkbutton(label="Сапфир", variable=var_sapphire, command=update_filters)
stone_menu.add_checkbutton(label="Рубин", variable=var_ruby, command=update_filters)
stone_menu.add_checkbutton(label="Изумруд", variable=var_emerald, command=update_filters)
stone_menu.add_checkbutton(label="Фианит", variable=var_cubic_zirconia, command=update_filters)
#по размеру
size_menu = tk.Menu(filter_menu, tearoff=0)
filter_menu.add_cascade(label="По размеру", menu=size_menu)

filter_menu.add_separator()
filter_menu.add_command(label="Сбросить фильтры", command=reset_filters, foreground="red")


#сортировки
sort_menu = tk.Menu(Menu, tearoff=0)
Menu.add_cascade(label="Сортировки", menu=sort_menu)
sort_menu.add_command(label="Сортировка от А до Я",command=lambda: set_sort("name ASC"))
sort_menu.add_command(label="Сортировка от Я до А",command=lambda: set_sort("name DESC"))
sort_menu.add_command(label="Сначала дешевые",command=lambda: set_sort("price ASC"))

sort_menu.add_separator()
sort_menu.add_command(label="Сбросить сортировку", command=reset_sorting,foreground="red")

delete = tk.Button(root, text="Удалить",bg="#2D6A4F", fg="white",width=25,command=delete_selected_item)
delete.grid(row=1, column=0, padx=500, pady=10, sticky="w")

otchet_menu = tk.Menu(Menu, tearoff=0)
Menu.add_cascade(label="Отчеты", menu=otchet_menu)

otchet_menu.add_checkbutton(label="1")


#покупка
buy = tk.Button(root,text="Купить изделие",bg="#2D6A4F", fg="white",command=open_buy_window)
buy.grid(row=1, column=0, padx=700, pady=10, sticky="w")

root.mainloop()