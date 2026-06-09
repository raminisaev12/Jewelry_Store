import flet as ft
import mysql.connector

def connect_to_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="diamond_path"
        )
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None

def main(page: ft.Page):
    page.title = "Алмазный путь"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.data = {"current_sort": ""}

    # --- Поля ввода ---
    f_name = ft.TextField(label="Название", width=300)
    f_type = ft.Dropdown(
        label="Тип",
        options=[ft.dropdown.Option(x) for x in ["Кольцо", "Серьги", "Браслет", "Цепочка"]],
        value="Кольцо",
        width=200
    )
    f_cat = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option(x) for x in ["Свадебные", "Женские", "Мужские", "Детские"]],
        width=200
    )
    f_metal = ft.Dropdown(
        label="Металл",
        options=[ft.dropdown.Option(x) for x in ["Золото (Красное)", "Золото (Белое)", "Золото (Желтое)", "Серебро"]],
        width=200
    )
    f_gem = ft.Dropdown(
        label="Камень",
        options=[ft.dropdown.Option(x) for x in ["Нет", "Бриллиант", "Сапфир", "Рубин", "Изумруд", "Фианит"]],
        width=200
    )
    f_purity = ft.TextField(label="Проба", width=150)
    f_weight = ft.TextField(label="Вес (г)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    f_price = ft.TextField(label="Цена (₽)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    f_size = ft.Dropdown(label="Размер", options=[], width=150)

    # --- Логика ---
    def clear_form():
        f_name.value = ""
        f_purity.value = ""
        f_weight.value = ""
        f_price.value = ""
        f_type.value = "Кольцо"
        f_cat.value = None
        f_metal.value = None
        f_gem.value = None
        update_size_options()

    def update_size_options(e=None):
        selected = f_type.value
        if selected == "Кольцо":
            sizes = ["15", "15.5", "16", "16.5", "17", "17.5", "18"]
        elif selected == "Браслет":
            sizes = ["16", "17", "18", "19", "20"]
        else:
            sizes = ["—"]
        f_size.options = [ft.dropdown.Option(s) for s in sizes]
        f_size.value = sizes[0]
        f_size.update()

    # --- Таблица ---
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Название")),
            ft.DataColumn(ft.Text("Тип")), ft.DataColumn(ft.Text("Категория")),
            ft.DataColumn(ft.Text("Металл")), ft.DataColumn(ft.Text("Камень")),
            ft.DataColumn(ft.Text("Проба")), ft.DataColumn(ft.Text("Вес")),
            ft.DataColumn(ft.Text("Цена")), ft.DataColumn(ft.Text("Размер")),
        ],
        rows=[]
    )

    def load_data(e=None):
        search = search_field.value
        t_filter = filter_type_dropdown.value
        m_filter = filter_metal_dropdown.value
        g_filter = filter_gem_dropdown.value

        data_table.rows.clear()
        conn = connect_to_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, type, category, metal, gemstone, purity, weight, price, size FROM jewelry_items WHERE 1=1"
            params = []
            if search:
                query += " AND name LIKE %s"
                params.append(f"%{search}%")
            if t_filter != "Все":
                query += " AND type = %s"
                params.append(t_filter)
            if m_filter != "Все":
                query += " AND metal = %s"
                params.append(m_filter)
            if g_filter != "Все":
                query += " AND gemstone = %s"
                params.append(g_filter)
            if page.data["current_sort"]:
                query += f" ORDER BY {page.data['current_sort']}"
            cursor.execute(query, params)
            for row in cursor.fetchall():
                data_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row]))
            cursor.close()
            conn.close()
        except Exception as ex:
            print(f"Ошибка загрузки: {ex}")
        page.update()

    def add_item_clicked(e):
        if not f_name.value or not f_price.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("Заполните название и цену!"))
            page.snack_bar.open = True
            page.update()
            return

        conn = connect_to_db()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("CALL AddJewelry(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (
                f_name.value, f_type.value, f_cat.value, f_metal.value,
                f_purity.value, f_weight.value, f_price.value, f_gem.value, f_size.value
            ))
            conn.commit()
            cursor.close()
            conn.close()

            page.snack_bar = ft.SnackBar(content=ft.Text("Успешно добавлено!"))
            page.snack_bar.open = True
            clear_form()
            page.update()
            load_data()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- Фильтры, поиск, сортировка (оставляем слева, не меняем) ---
    search_field = ft.TextField(label="Поиск по названию...", expand=True)
    filter_type_dropdown = ft.Dropdown(
        label="Тип",
        options=[ft.dropdown.Option(x) for x in ["Все", "Кольцо", "Серьги", "Браслет", "Цепочка"]],
        value="Все", width=130
    )
    filter_metal_dropdown = ft.Dropdown(
        label="Металл",
        options=[ft.dropdown.Option(x) for x in ["Все", "Золото (Красное)", "Золото (Белое)", "Золото (Желтое)", "Серебро"]],
        value="Все", width=130
    )
    filter_gem_dropdown = ft.Dropdown(
        label="Камень",
        options=[ft.dropdown.Option(x) for x in ["Все", "Нет", "Бриллиант", "Сапфир", "Рубин", "Изумруд", "Фианит"]],
        value="Все", width=130
    )

    sort_menu = ft.PopupMenuButton(
        icon="sort",
        items=[
            ft.PopupMenuItem(content=ft.Text("Сначала дешевые"), on_click=lambda _: (page.data.update({"current_sort": "price ASC"}), load_data())),
            ft.PopupMenuItem(content=ft.Text("Сначала дорогие"), on_click=lambda _: (page.data.update({"current_sort": "price DESC"}), load_data())),
            ft.PopupMenuItem(content=ft.Text("От А до Я"), on_click=lambda _: (page.data.update({"current_sort": "name ASC"}), load_data())),
            ft.PopupMenuItem(content=ft.Text("От Я до А"), on_click=lambda _: (page.data.update({"current_sort": "name DESC"}), load_data())),
            ft.PopupMenuItem(content=ft.Text("Сначала тяжелые"), on_click=lambda _: (page.data.update({"current_sort": "weight DESC"}), load_data())),
            ft.PopupMenuItem(content=ft.Text("Сначала легкие"), on_click=lambda _: (page.data.update({"current_sort": "weight ASC"}), load_data())),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(content=ft.Text("Сбросить сортировку"), on_click=lambda _: (page.data.update({"current_sort": ""}), load_data())),
        ]
    )

    search_field.on_change = load_data
    filter_type_dropdown.on_change = load_data
    filter_metal_dropdown.on_change = load_data
    filter_gem_dropdown.on_change = load_data

    def reset_all_filters(e):
        search_field.value = ""
        filter_type_dropdown.value = "Все"
        filter_metal_dropdown.value = "Все"
        filter_gem_dropdown.value = "Все"
        page.data["current_sort"] = ""
        page.update()
        load_data()

    # --- Интерфейс ---
    # Заголовок (слева)
    header = ft.Row([
        ft.Image(src="logo.png", width=50, height=50),
        ft.Text("Алмазный путь", size=24, weight="bold")
    ], alignment=ft.MainAxisAlignment.START)

    # Форма добавления: правильный порядок, все строки центрированы
    add_form = ft.Column(
        [
            ft.Row([f_name], alignment=ft.MainAxisAlignment.CENTER),                                   # Название
            ft.Row([f_type, ft.FilledButton("Применить тип", icon="check", on_click=update_size_options)],
                   alignment=ft.MainAxisAlignment.CENTER),                                            # Тип + кнопка
            ft.Row([f_cat], alignment=ft.MainAxisAlignment.CENTER),                                   # Категория
            ft.Row([f_metal], alignment=ft.MainAxisAlignment.CENTER),                                 # Металл
            ft.Row([f_gem], alignment=ft.MainAxisAlignment.CENTER),                                   # Камень
            ft.Row([f_purity], alignment=ft.MainAxisAlignment.CENTER),                                # Проба
            ft.Row([f_weight], alignment=ft.MainAxisAlignment.CENTER),                                # Вес
            ft.Row([f_price], alignment=ft.MainAxisAlignment.CENTER),                                 # Цена
            ft.Row([f_size], alignment=ft.MainAxisAlignment.CENTER),                                  # Размер
            ft.Row([ft.FilledButton("Сохранить", on_click=add_item_clicked, icon="add")],
                   alignment=ft.MainAxisAlignment.CENTER),                                           # Кнопка сохранить
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    page.add(
        header,
        ft.ExpansionTile(
            title=ft.Text("Добавить изделие"),
            subtitle=ft.Text("Нажмите для заполнения формы"),
            controls=[add_form],
            expanded=True
        ),
        ft.Divider(),
        ft.Row([search_field, sort_menu], alignment=ft.MainAxisAlignment.START),
        ft.Row([filter_type_dropdown, filter_metal_dropdown, filter_gem_dropdown,
                ft.FilledButton("Сбросить фильтры", on_click=reset_all_filters, icon="refresh")],
               alignment=ft.MainAxisAlignment.START),
        ft.Container(content=data_table, padding=10)
    )

    update_size_options()
    load_data()

if __name__ == "__main__":
    try:
        ft.run(main)
    except TypeError:
        ft.app(target=main)