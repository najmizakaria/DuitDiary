import math
from tkinter import messagebox
import sqlite3
import tkinter as tk
from datetime import date

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
window.geometry("700x450")

title = tk.Label(window, text="DuitDiary", font=("arial", 20))
title.pack(pady=20)

form = tk.Frame(window)
form.pack(pady=10)

tk.Label(form, text="Type").grid(row=0, column=0, padx=5, pady=5)
type_var = tk.StringVar(value="Expense")
tk.OptionMenu(form, type_var, "Expense", "Income").grid(row=0, column=1)

tk.Label(form, text="Category").grid(row=1, column=0, padx=5, pady=5)
category_entry =tk.Entry(form)
category_entry.grid(row=1, column=1)

tk.Label(form, text="Amount").grid(row=2, column=0, padx=5, pady=5)
amount_entry = tk.Entry(form)
amount_entry.grid(row=2, column=1)

tk.Label(form, text="Date (YYYY-MM-DD)").grid(row=3, column=0, padx=5, pady=5)
date_entry =tk.Entry(form)
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

    messagebox.showinfo("Saved", "Transaction saved.")
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

tk.Button(window, text="Save Transaction", command=save_transaction).pack(pady=10)

window.mainloop()