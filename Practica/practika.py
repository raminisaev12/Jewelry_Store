import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


root = tk.Tk()
root.title("Алмазный путь")
root.geometry("600x400")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


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
border_frame.grid(row=1, column=0, padx=20, pady=10, sticky="w")

#
dobavl = tk.Label(border_frame, text="Добавление изделия", fg="#4A7C59",
                  font=("Segoe UI", 12, "italic"), bg=bg_color)
dobavl.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

#
Label_name = tk.Label(border_frame,text="Название изделия", bg=bg_color)
Label_name.grid(row=1, column=0, padx=0, pady=10, sticky="w")
Entry_viborka = ttk.Entry(border_frame)
Entry_viborka.grid(row=1, column=0, padx=105, pady=10, sticky="w")

####скелет
cols = ('name', 'category', 'metal', 'purity','weight', 'price')

tree = ttk.Treeview(root, columns=cols, show='headings',height=8)

tree.heading('name', text='Название изделия')
tree.heading('category', text='Категория')
tree.heading('metal', text='Металл')
tree.heading('purity', text='Проба')
tree.heading('weight', text='Вес (г)')
tree.heading('price', text='Цена (₽)')

for col in cols:
    tree.column(col,width=100)

tree.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

root.mainloop()