import math
import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk


def setup_database():
    connection = sqlite3.connect("duitdiary.db")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    """)
    connection.commit()
    connection.close()


setup_database()

window = tk.Tk()
window.title("DuitDiary")
window.geometry("850x600")

title = tk.Label(window, text="DuitDiary", font=("Arial", 20))
title.pack(pady=20)

form = tk.Frame(window)
form.pack(pady=10)

tk.Label(form, text="Type").grid(row=0, column=0, padx=5, pady=5)
type_var = tk.StringVar(value="Expense")
tk.OptionMenu(form, type_var, "Expense", "Income").grid(row=0, column=1)

tk.Label(form, text="Category").grid(row=1, column=0, padx=5, pady=5)
category_entry = tk.Entry(form)
category_entry.grid(row=1, column=1)

tk.Label(form, text="Amount").grid(row=2, column=0, padx=5, pady=5)
amount_entry = tk.Entry(form)
amount_entry.grid(row=2, column=1)

tk.Label(form, text="Date (YYYY-MM-DD)").grid(row=3, column=0, padx=5, pady=5)
date_entry = tk.Entry(form)
date_entry.insert(0, date.today().isoformat())
date_entry.grid(row=3, column=1)

tk.Label(form, text="Description").grid(row=4, column=0, padx=5, pady=5)
description_entry = tk.Entry(form)
description_entry.grid(row=4, column=1)


def save_transaction():
    category = category_entry.get().strip()
    amount_text = amount_entry.get().strip()
    date_text = date_entry.get().strip()
    description = description_entry.get().strip()

    if not category:
        messagebox.showerror("Invalid entry", "Enter a category.")
        return

    try:
        amount = float(amount_text)
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid entry", "Enter an amount greater than zero.")
        return

    try:
        date.fromisoformat(date_text)
    except ValueError:
        messagebox.showerror("Invalid entry", "Enter a valid date as YYYY-MM-DD.")
        return

    connection = sqlite3.connect("duitdiary.db")
    connection.execute(
        """INSERT INTO transactions
           (transaction_type, category, amount, date, description)
           VALUES (?, ?, ?, ?, ?)""",
        (type_var.get(), category, amount, date_text, description),
    )
    connection.commit()
    connection.close()

    load_transactions()
    messagebox.showinfo("Saved", "Transaction saved.")

    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)


tk.Button(
    window,
    text="Save Transaction",
    command=save_transaction,
).pack(pady=10)

search_frame = tk.Frame(window)
search_frame.pack(pady=5)

tk.Label(search_frame, text="Search").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

tk.Button(
    search_frame,
    text="Search",
    command=lambda: load_transactions(),
).pack(side=tk.LEFT)

transactions_table = ttk.Treeview(
    window,
    columns=("Date", "Type", "Category", "Amount", "Description"),
    show="headings",
    height=10,
)

for column in ("Date", "Type", "Category", "Amount", "Description"):
    transactions_table.heading(column, text=column)

transactions_table.pack(pady=10)


def load_transactions():
    search = f"%{search_entry.get().strip()}%"

    connection = sqlite3.connect("duitdiary.db")
    rows = connection.execute(
        """SELECT id, transaction_type, category, amount, date, description
           FROM transactions
           WHERE transaction_type LIKE ?
                OR category LIKE ?
                OR date LIKE ?
                OR description LIKE ?
           ORDER BY date DESC, id DESC""",
        (search, search, search, search),
    ).fetchall()
    connection.close()

    for item in transactions_table.get_children():
        transactions_table.delete(item)

    for row in rows:
        transactions_table.insert(
            "",
            tk.END,
            iid=str(row[0]),
            values=(row[4], row[1], row[2], f"{row[3]:.2f}", row[5]),
        )


load_transactions()

def delete_transaction():
    selected = transactions_table.selection()

    if not selected:
        messagebox.showwarning("No selection", "Select a transaction first.")
        return

    if not messagebox.askyesno("Confirm delete", "Delete this transaction?"):
        return

    transaction_id =int(selected[0])

    connection = sqlite3.connect("duitdiary.db")
    connection.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,),
    )
    connection.commit()
    connection.close()

    load_transactions()

tk.Button(
    window,
    text="Delete Selected",
    command=delete_transaction,
).pack(pady=5)

window.mainloop()