import flet as ft
import mysql.connector
import random
from datetime import date
from docx import Document
from docx.shared import Inches
from docx.enum.section import WD_ORIENT
import os
import tempfile

# ---------- Подключение к БД ----------
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="localhost",      # замени на IP ПК при тесте с телефона
            user="root",
            password="1234",
            database="diamond_path"
        )
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None

def get_distinct_values(column):
    conn = connect_to_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT {column} FROM jewelry_items WHERE {column} IS NOT NULL AND {column} != '' ORDER BY {column}")
        rows = cursor.fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        print(e)
        return []
    finally:
        conn.close()

def main(page: ft.Page):
    page.title = "Алмазный путь"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.data = {"current_sort": "", "selected_item": None}

    # ---------- Поля ввода (добавление) ----------
    f_name = ft.TextField(label="Название", expand=True,
                          input_filter=ft.InputFilter(allow=True, regex_string=r"[А-Яа-яA-Za-z\s\-]+"))
    f_type = ft.Dropdown(
        label="Тип",
        options=[ft.dropdown.Option(x) for x in ["Кольцо", "Серьги", "Браслет", "Цепочка"]],
        value="Кольцо", expand=True
    )
    f_cat = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option(x) for x in ["Свадебные", "Женские", "Мужские", "Детские"]],
        expand=True
    )
    f_metal = ft.Dropdown(
        label="Металл",
        options=[ft.dropdown.Option(x) for x in ["Золото", "Красное золото", "Белое золото", "Желтое золото", "Серебро"]],
        expand=True
    )
    f_gem = ft.Dropdown(
        label="Камень",
        options=[ft.dropdown.Option(x) for x in ["Нет", "Бриллиант", "Сапфир", "Рубин", "Изумруд", "Фианит"]],
        expand=True
    )
    f_purity = ft.Dropdown(
        label="Проба",
        options=[ft.dropdown.Option(x) for x in ["375", "500", "585", "750", "925", "958", "999"]],
        expand=True
    )
    f_weight = ft.TextField(label="Вес (г)", keyboard_type=ft.KeyboardType.NUMBER, expand=True,
                            input_filter=ft.InputFilter(allow=True, regex_string=r"\d*\.?\d*"))
    f_price = ft.TextField(label="Цена (₽)", keyboard_type=ft.KeyboardType.NUMBER, expand=True,
                           input_filter=ft.InputFilter(allow=True, regex_string=r"\d*\.?\d*"))
    f_size = ft.Dropdown(label="Размер", options=[], expand=True)
    f_quantity = ft.TextField(label="Количество", keyboard_type=ft.KeyboardType.NUMBER, value="1", expand=True,
                              input_filter=ft.InputFilter(allow=True, regex_string=r"\d+"))

    # ----- Функция обновления размеров -----
    def update_size_options(e=None):
        selected = f_type.value
        if selected == "Кольцо":
            sizes = ["15", "15.5", "16", "16.5", "17", "17.5", "18", "18.5", "19"]
        elif selected == "Браслет":
            sizes = ["16", "17", "18", "19", "20"]
        elif selected == "Цепочка":
            sizes = ["40", "45", "50", "55", "60", "65"]
        else:
            sizes = ["—"]
        f_size.options = [ft.dropdown.Option(s) for s in sizes]
        f_size.value = sizes[0]
        page.update()

    update_size_options()

    def clear_form():
        f_name.value = ""
        f_weight.value = ""
        f_price.value = ""
        f_quantity.value = "1"
        f_purity.value = None
        f_cat.value = None
        f_metal.value = None
        f_gem.value = None
        f_type.value = "Кольцо"
        update_size_options()

    # ---------- Таблица (показывается отдельно) ----------
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Название")),
            ft.DataColumn(ft.Text("Тип")), ft.DataColumn(ft.Text("Категория")),
            ft.DataColumn(ft.Text("Металл")), ft.DataColumn(ft.Text("Камень")),
            ft.DataColumn(ft.Text("Проба")), ft.DataColumn(ft.Text("Вес")),
            ft.DataColumn(ft.Text("Цена")), ft.DataColumn(ft.Text("Размер")),
            ft.DataColumn(ft.Text("Кол-во"))
        ],
        rows=[], expand=True,
        column_spacing=10,
        heading_row_height=40, data_row_min_height=35,
        heading_text_style=ft.TextStyle(size=12),
        data_text_style=ft.TextStyle(size=11)
    )

    # ---------- Поиск и фильтры ----------
    search_field = ft.TextField(label="Поиск по названию...", expand=True)
    filter_type = ft.Dropdown(label="Тип", width=120)
    filter_cat = ft.Dropdown(label="Категория", width=120)
    filter_metal = ft.Dropdown(label="Металл", width=120)
    filter_gem = ft.Dropdown(label="Камень", width=120)
    filter_size = ft.Dropdown(label="Размер", width=120)
    filter_purity = ft.Dropdown(label="Проба", width=120)

    def load_filter_values():
        filter_type.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("type")]
        filter_cat.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("category")]
        filter_metal.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("metal")]
        filter_gem.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("gemstone")]
        filter_size.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("size")]
        filter_purity.options = [ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in get_distinct_values("purity")]
        for dd in [filter_type, filter_cat, filter_metal, filter_gem, filter_size, filter_purity]:
            dd.value = "Все"
        page.update()
    load_filter_values()

    def load_data():
        data_table.rows.clear()
        search = search_field.value
        filters = {
            "type": filter_type.value if filter_type.value != "Все" else None,
            "category": filter_cat.value if filter_cat.value != "Все" else None,
            "metal": filter_metal.value if filter_metal.value != "Все" else None,
            "gemstone": filter_gem.value if filter_gem.value != "Все" else None,
            "size": filter_size.value if filter_size.value != "Все" else None,
            "purity": filter_purity.value if filter_purity.value != "Все" else None,
        }
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, type, category, metal, gemstone, purity, weight, price, size, quantity FROM jewelry_items WHERE 1=1"
            params = []
            if search:
                query += " AND name LIKE %s"
                params.append(f"%{search}%")
            for col, val in filters.items():
                if val:
                    query += f" AND {col} = %s"
                    params.append(val)
            if page.data["current_sort"]:
                query += f" ORDER BY {page.data['current_sort']}"
            cursor.execute(query, params)
            for row in cursor.fetchall():
                data_table.rows.append(ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(val))) for val in row],
                    on_select_change=lambda e, r=row: select_item(r)
                ))
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        page.update()

    search_field.on_change = lambda _: load_data()
    for dd in [filter_type, filter_cat, filter_metal, filter_gem, filter_size, filter_purity]:
        dd.on_change = lambda _: load_data()

    def select_item(row):
        page.data["selected_item"] = row

    # ---------- Действия ----------
    def add_item(e):
        if not f_name.value or not f_price.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("Заполните название и цену!"))
            page.snack_bar.open = True
            page.update()
            return
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("CALL AddJewelry(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                f_name.value, f_type.value, f_cat.value, f_metal.value,
                f_purity.value, f_weight.value, f_quantity.value, f_price.value,
                f_gem.value, f_size.value
            ))
            conn.commit()
            cursor.close()
            conn.close()
            clear_form()
            page.snack_bar = ft.SnackBar(content=ft.Text("Товар добавлен!"))
            page.snack_bar.open = True
            load_data()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка: {ex}"))
            page.snack_bar.open = True
            page.update()

    def delete_item(e):
        selected = page.data["selected_item"]
        if not selected:
            page.snack_bar = ft.SnackBar(content=ft.Text("Выберите товар в таблице!"))
            page.snack_bar.open = True
            page.update()
            return
        item_id = selected[0]
        def confirm_delete(ok):
            if not ok:
                return
            conn = connect_to_db()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM jewelry_items WHERE id = %s", (item_id,))
                conn.commit()
                cursor.close()
                conn.close()
                page.data["selected_item"] = None
                page.snack_bar = ft.SnackBar(content=ft.Text("Удалено"))
                page.snack_bar.open = True
                load_data()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка удаления: {ex}"))
                page.snack_bar.open = True
                page.update()
        page.dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение"),
            content=ft.Text(f"Удалить товар с ID {item_id}?"),
            actions=[
                ft.TextButton("Да", on_click=lambda _: (page.dialog.dismiss(), confirm_delete(True))),
                ft.TextButton("Нет", on_click=lambda _: (page.dialog.dismiss(), confirm_delete(False)))
            ]
        )
        page.dialog.open = True
        page.update()

    def open_buy_dialog(e):
        """Покупка (продажа со склада)"""
        selected = page.data["selected_item"]
        if not selected:
            page.snack_bar = ft.SnackBar(content=ft.Text("Выберите товар в таблице!"))
            page.snack_bar.open = True
            page.update()
            return
        item_id = selected[0]
        item_name = selected[1]
        price = float(selected[8])      # цена из колонки с индексом 8
        stock = int(selected[10])       # остаток из колонки с индексом 10

        seller_dd = ft.Dropdown(
            label="Продавец",
            options=[ft.dropdown.Option(x) for x in ["Иванов И.И.", "Петров П.П.", "Сидорова А.А."]],
            value="Иванов И.И.", width=200
        )
        qty_field = ft.TextField(label="Количество", value="1",
                                 keyboard_type=ft.KeyboardType.NUMBER,
                                 input_filter=ft.InputFilter(allow=True, regex_string=r"\d+"))
        payment_dd = ft.Dropdown(
            label="Оплата",
            options=[ft.dropdown.Option(x) for x in ["Наличные", "Карта", "Перевод"]],
            value="Наличные", width=150
        )
        total_text = ft.Text(f"Итого: {price:.2f} ₽", size=16, color=ft.Colors.GREEN)

        def recalc_total(*args):
            qty = int(qty_field.value) if qty_field.value.isdigit() else 0
            total = qty * price
            total_text.value = f"Итого: {total:.2f} ₽"
            page.update()

        qty_field.on_change = recalc_total

        def confirm_purchase(e):
            qty_str = qty_field.value
            if not qty_str.isdigit() or int(qty_str) <= 0:
                page.snack_bar = ft.SnackBar(content=ft.Text("Неверное количество"))
                page.snack_bar.open = True
                page.update()
                return
            qty = int(qty_str)
            if qty > stock:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"На складе только {stock} шт."))
                page.snack_bar.open = True
                page.update()
                return
            total = qty * price
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE jewelry_items SET quantity = quantity - %s WHERE id = %s", (qty, item_id))
                cursor.execute("""
                    INSERT INTO sales_history (seller_name, item_name, quantity_sold, price_per_item, payment_method, total_price)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (seller_dd.value, item_name, qty, price, payment_dd.value, total))
                conn.commit()
                cursor.close()
                conn.close()
                page.dialog.dismiss()
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Продажа: {item_name} x{qty}"))
                page.snack_bar.open = True
                load_data()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Ошибка продажи: {ex}"))
                page.snack_bar.open = True
                page.update()

        content = ft.Column([
            ft.Text(f"Товар: {item_name}", weight="bold"),
            ft.Text(f"Цена за шт.: {price:.2f} ₽"),
            ft.Text(f"В наличии: {stock} шт."),
            seller_dd, qty_field, payment_dd, total_text
        ], spacing=15, tight=True)
        page.dialog = ft.AlertDialog(
            title=ft.Text("Оформление продажи"),
            content=content,
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: page.dialog.dismiss()),
                ft.TextButton("Продать", on_click=confirm_purchase)
            ]
        )
        page.dialog.open = True
        page.update()

    # ---------- Каскадное меню сортировки ----------
    sort_button = ft.PopupMenuButton(
        content=ft.Text("Сортировка"),
        items=[
            ft.PopupMenuItem(
                content=ft.Text("Сначала дешевые"),
                on_click=lambda _: (page.data.update({"current_sort": "price ASC"}), load_data())
            ),
            ft.PopupMenuItem(
                content=ft.Text("Сначала дорогие"),
                on_click=lambda _: (page.data.update({"current_sort": "price DESC"}), load_data())
            ),
            ft.PopupMenuItem(
                content=ft.Text("От А до Я"),
                on_click=lambda _: (page.data.update({"current_sort": "name ASC"}), load_data())
            ),
            ft.PopupMenuItem(
                content=ft.Text("От Я до А"),
                on_click=lambda _: (page.data.update({"current_sort": "name DESC"}), load_data())
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                content=ft.Text("Сбросить сортировку"),
                on_click=lambda _: (page.data.update({"current_sort": ""}), load_data())
            ),
        ]
    )

    # ---------- Отчёты ----------
    report_date_from = ft.TextField(label="С", width=120, hint_text="ГГГГ-ММ-ДД")
    report_date_to = ft.TextField(label="По", width=120, hint_text="ГГГГ-ММ-ДД")
    report_seller = ft.Dropdown(
        label="Продавец",
        options=[ft.dropdown.Option(x) for x in ["Все", "Иванов И.И.", "Петров П.П.", "Сидорова А.А."]],
        value="Все", width=150
    )
    report_cat = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in ["Свадебные", "Женские", "Мужские", "Детские"]],
        value="Все", width=150
    )
    report_mat = ft.Dropdown(
        label="Материал",
        options=[ft.dropdown.Option("Все")] + [ft.dropdown.Option(x) for x in ["Золото", "Красное золото", "Белое золото", "Желтое золото", "Серебро"]],
        value="Все", width=150
    )
    report_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Дата")),
            ft.DataColumn(ft.Text("Продавец")), ft.DataColumn(ft.Text("Товар")),
            ft.DataColumn(ft.Text("Мат.")), ft.DataColumn(ft.Text("Кат.")),
            ft.DataColumn(ft.Text("Кол-во")), ft.DataColumn(ft.Text("Цена")),
            ft.DataColumn(ft.Text("Оплата")), ft.DataColumn(ft.Text("Итого"))
        ],
        rows=[], expand=True,
        column_spacing=10,
        heading_row_height=40, data_row_min_height=35
    )
    report_summary = ft.Text("", size=16, weight="bold")

    def load_reports(popular=False):
        report_table.rows.clear()
        start = report_date_from.value
        end = report_date_to.value
        seller = report_seller.value
        category = report_cat.value
        material = report_mat.value
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            if popular:
                query = """
                    SELECT CONCAT(MAX(j.prefix), '-', MIN(j.id)) as full_id,
                           DATE_FORMAT(MAX(s.sale_date), '%Y-%m-%d') as sale_date,
                           '—' as seller_name, s.item_name,
                           j.metal, j.category,
                           SUM(s.quantity_sold) as total_qty,
                           AVG(s.price_per_item) as price,
                           '—' as payment_method,
                           SUM(s.total_price) as total_price
                    FROM sales_history s
                    JOIN jewelry_items j ON s.item_name = j.name
                    WHERE 1=1
                """
                params = []
                if start: query += " AND s.sale_date >= %s"; params.append(start)
                if end: query += " AND s.sale_date <= %s"; params.append(end)
                query += " GROUP BY j.id, s.item_name, j.metal, j.category ORDER BY total_qty DESC"
            else:
                query = """
                    SELECT s.id, s.sale_date, s.seller_name, s.item_name,
                           j.metal, j.category,
                           s.quantity_sold, s.price_per_item, s.payment_method, s.total_price
                    FROM sales_history s
                    LEFT JOIN jewelry_items j ON s.item_name = j.name
                    WHERE 1=1
                """
                params = []
                if start: query += " AND s.sale_date >= %s"; params.append(start)
                if end: query += " AND s.sale_date <= %s"; params.append(end)
                if seller != "Все": query += " AND s.seller_name = %s"; params.append(seller)
                if category != "Все": query += " AND j.category = %s"; params.append(category)
                if material != "Все": query += " AND j.metal = %s"; params.append(material)
                query += " ORDER BY s.sale_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            total_sum = total_qty = 0
            for r in rows:
                report_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r.get('full_id', r.get('id'))))),
                    ft.DataCell(ft.Text(str(r.get('sale_date', '')))),
                    ft.DataCell(ft.Text(str(r.get('seller_name', '')))),
                    ft.DataCell(ft.Text(str(r.get('item_name', '')))),
                    ft.DataCell(ft.Text(str(r.get('metal', '—')))),
                    ft.DataCell(ft.Text(str(r.get('category', '—')))),
                    ft.DataCell(ft.Text(str(r.get('quantity_sold', r.get('total_qty', 0))))),
                    ft.DataCell(ft.Text(f"{r.get('price_per_item', r.get('price', 0)):.2f}")),
                    ft.DataCell(ft.Text(str(r.get('payment_method', '—')))),
                    ft.DataCell(ft.Text(f"{r.get('total_price', 0):.2f}"))
                ]))
                total_sum += r.get('total_price', 0)
                total_qty += r.get('quantity_sold', r.get('total_qty', 0))
            report_summary.value = f"💰 Выручка: {total_sum:,.2f} руб. | 📦 Продано: {total_qty} шт."
            cursor.close()
            conn.close()
        except Exception as ex:
            print(ex)
        page.update()

    def load_efficiency():
        report_table.rows.clear()
        start = report_date_from.value
        end = report_date_to.value
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT seller_name, COUNT(*) as sales_count,
                       SUM(quantity_sold) as total_qty,
                       SUM(total_price) as total_revenue
                FROM sales_history
                WHERE 1=1
            """
            params = []
            if start: query += " AND sale_date >= %s"; params.append(start)
            if end: query += " AND sale_date <= %s"; params.append(end)
            query += " GROUP BY seller_name ORDER BY total_revenue DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            for r in rows:
                report_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text("—")), ft.DataCell(ft.Text("—")),
                    ft.DataCell(ft.Text(r['seller_name'])), ft.DataCell(ft.Text("—")),
                    ft.DataCell(ft.Text("—")), ft.DataCell(ft.Text("—")),
                    ft.DataCell(ft.Text(str(r['total_qty']))),
                    ft.DataCell(ft.Text("—")), ft.DataCell(ft.Text("—")),
                    ft.DataCell(ft.Text(f"{r['total_revenue']:.2f}"))
                ]))
            report_summary.value = "📊 Отчет по эффективности сотрудников"
            cursor.close()
            conn.close()
        except Exception as ex:
            print(ex)
        page.update()

    def save_report_to_docx(e):
        rows_data = [row.cells for row in report_table.rows]
        if not rows_data:
            page.snack_bar = ft.SnackBar(content=ft.Text("Нет данных для отчёта"))
            page.snack_bar.open = True
            page.update()
            return
        doc = Document()
        section = doc.sections[0]
        new_width, new_height = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = new_width
        section.page_height = new_height
        doc.add_heading("Отчёт по продажам", 0)
        table = doc.add_table(rows=1, cols=10)
        table.style = "Table Grid"
        table.autofit = False
        table.allow_autofit = False
        widths = [0.5, 0.9, 0.8, 0.9, 0.8, 0.8, 0.7, 0.7, 0.8, 0.8]
        headers = ['ID','Дата','Продавец','Товар','Материал','Категория','Кол-во','Цена','Оплата','Итого']
        hdr = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = h
            table.columns[i].width = Inches(widths[i])
        for row_cells in rows_data:
            r = table.add_row().cells
            for i, cell in enumerate(row_cells):
                r[i].text = str(cell.content.value)
        file_path = os.path.join(tempfile.gettempdir(), "report.docx")
        doc.save(file_path)
        try:
            import webbrowser
            webbrowser.open(file_path)
        except:
            pass
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Файл сохранён: {file_path}"))
        page.snack_bar.open = True
        page.update()

    # ---------- Переключение на просмотр таблицы ----------
    def show_table_view(e=None):
        load_data()
        page.data["previous_view"] = page.controls[1] if len(page.controls) > 1 else None
        page.controls.clear()
        page.add(
            ft.Row([
                ft.TextButton("← Назад", on_click=hide_table_view),
                ft.Text("Список изделий", size=18, weight="bold")
            ]),
            ft.Container(content=data_table, expand=True, padding=5)
        )
        page.update()

    def hide_table_view(e=None):
        previous = page.data.get("previous_view")
        page.controls.clear()
        page.add(nav_bar, previous if previous else catalog_view)
        page.update()

    # ---------- Компоновка каталога ----------
    catalog_view = ft.Column([
        ft.Row([search_field, sort_button]),   # <-- МЕНЮ СОРТИРОВКИ
        ft.Row([filter_type, filter_cat, filter_metal, filter_gem, filter_size, filter_purity,
                ft.Button("Сброс фильтров", on_click=lambda _: (load_filter_values(), load_data()))],
               wrap=True),
        ft.Divider(),
        ft.Text("Добавить изделие", size=16, weight="bold"),
        ft.Column([
            ft.Row([f_name]),
            ft.Row([f_type, ft.Button("Применить тип", on_click=update_size_options)]),
            ft.Row([f_cat]),
            ft.Row([f_metal]),
            ft.Row([f_gem]),
            ft.Row([f_purity]),
            ft.Row([f_weight]),
            ft.Row([f_price]),
            ft.Row([f_size]),
            ft.Row([f_quantity]),
        ], tight=True, spacing=5),
        ft.Row([
            ft.Button("➕ Добавить", on_click=add_item),
            ft.Button("🗑 Удалить", on_click=delete_item),
            ft.Button("🛒 Купить", on_click=open_buy_dialog),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Divider(),
        ft.Button("📋 Показать таблицу изделий", on_click=show_table_view, expand=True)
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    reports_view = ft.Column([
        ft.Text("Отчёты", size=20, weight="bold"),
        ft.Row([report_date_from, report_date_to, report_seller, report_cat, report_mat],
               wrap=True),
        ft.Row([
            ft.Button("Обновить", on_click=lambda _: load_reports(False)),
            ft.Button("Популярность", on_click=lambda _: load_reports(True)),
            ft.Button("Эффективность", on_click=lambda _: load_efficiency()),
            ft.Button("💾 Word", on_click=save_report_to_docx)
        ], wrap=True),
        ft.Container(content=report_table, expand=True, padding=5),
        report_summary
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    def switch_to_catalog(e):
        page.controls.clear()
        page.add(nav_bar, catalog_view)
        page.update()

    def switch_to_reports(e):
        page.controls.clear()
        page.add(nav_bar, reports_view)
        load_reports(False)
        page.update()

    nav_bar = ft.Row([
        ft.Button("Каталог", on_click=switch_to_catalog),
        ft.Button("Отчёты", on_click=switch_to_reports)
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.add(nav_bar, catalog_view)
    load_data()
    page.update()

if __name__ == "__main__":
    ft.run(main)