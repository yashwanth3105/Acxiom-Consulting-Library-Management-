# ==========================================================
# Library Management System
# ==========================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

# ==========================================================
# DATABASE SETUP
# ==========================================================

conn = sqlite3.connect("library_perfect_final.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    category TEXT,
    available INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS members(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    duration TEXT,
    active INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS issues(
    serial_no INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    member_id INTEGER,
    issue_date TEXT,
    return_date TEXT,
    returned INTEGER DEFAULT 0,
    fine_paid INTEGER DEFAULT 0,
    fine_amount REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS issue_requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    member_id INTEGER,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fine_payments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_no INTEGER,
    amount REAL,
    payment_date TEXT
)
""")

cursor.execute("INSERT OR IGNORE INTO users VALUES('admin','admin123','admin')")
cursor.execute("INSERT OR IGNORE INTO users VALUES('user','user123','user')")
conn.commit()

# ==========================================================
# ROOT WINDOW
# ==========================================================

root = tk.Tk()
root.lift()
root.attributes('-topmost', True)
root.after(1000, lambda: root.attributes('-topmost', False))
root.title("Library Management System")
root.geometry("900x600")

# ==========================================================
# UTILITIES
# ==========================================================

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def restart_app():
    clear_window()
    show_login_screen()

# ==========================================================
# LOGIN SYSTEM
# ==========================================================

def login():
    uname = username_entry.get()
    pwd = password_entry.get()
    role = role_var.get()

    cursor.execute("""
    SELECT * FROM users WHERE username=? AND password=? AND role=?
    """, (uname, pwd, role))

    if cursor.fetchone():
        if role == "admin":
            admin_dashboard()
        else:
            user_dashboard()
    else:
        messagebox.showerror("Error", "Invalid Credentials")

# ==========================================================
# LOGIN SCREEN
# ==========================================================

def show_login_screen():
    global username_entry, password_entry, role_var

    frame = tk.Frame(root)
    frame.pack(pady=150)

    tk.Label(frame, text="Library Management Login",
             font=("Arial", 22)).grid(row=0, columnspan=2, pady=20)

    tk.Label(frame, text="Username").grid(row=1, column=0)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=1, column=1)

    tk.Label(frame, text="Password").grid(row=2, column=0)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=2, column=1)

    tk.Label(frame, text="Role").grid(row=3, column=0)
    role_var = ttk.Combobox(frame, values=["admin", "user"])
    role_var.grid(row=3, column=1)
    role_var.current(0)

    tk.Button(frame, text="Login", command=login).grid(row=4, columnspan=2, pady=20)

# ==========================================================
# DASHBOARDS
# ==========================================================

def admin_dashboard():
    clear_window()
    tk.Label(root, text="Admin Dashboard",
             font=("Arial", 20)).pack(pady=20)

    buttons = [
        ("Add Book", add_book_window),
        ("Update Book", update_book_window),
        ("Add Membership", add_membership_window),
        ("Update Membership", update_membership_window),
        ("Cancel Membership", cancel_membership_window),
        ("User Management", user_management_window),
        ("Reports", reports_window),
        ("Logout", restart_app)
    ]

    for txt, cmd in buttons:
        tk.Button(root, text=txt, width=30, command=cmd).pack(pady=5)

def user_dashboard():
    clear_window()
    tk.Label(root, text="User Dashboard",
             font=("Arial", 20)).pack(pady=20)

    buttons = [
        ("Search Books", search_books_window),
        ("Issue Book", issue_book_window),
        ("Return Book", return_book_window),
        ("Fine Payment", fine_payment_window),
        ("Reports", reports_window),
        ("Logout", restart_app)
    ]

    for txt, cmd in buttons:
        tk.Button(root, text=txt, width=30, command=cmd).pack(pady=5)

# ==========================================================
# BOOK MANAGEMENT
# ==========================================================

def add_book_window():
    win = tk.Toplevel(root)
    win.title("Add Book")

    labels = ["Title", "Author", "Category(Book/Movie)"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0)
        e = tk.Entry(win)
        e.grid(row=i, column=1)
        entries.append(e)

    def save():
        if any(not e.get().strip() for e in entries):
            messagebox.showerror("Error", "All fields required")
            return

        cursor.execute("""
        INSERT INTO books(title,author,category)
        VALUES(?,?,?)
        """, (
            entries[0].get(),
            entries[1].get(),
            entries[2].get()
        ))
        conn.commit()
        messagebox.showinfo("Success", "Book Added Successfully")
        win.destroy()

    tk.Button(win, text="Save", command=save).grid(row=4, columnspan=2)

def update_book_window():
    win = tk.Toplevel(root)
    win.title("Update Book")

    labels = ["Book ID", "New Title", "New Author", "New Category"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0)
        e = tk.Entry(win)
        e.grid(row=i, column=1)
        entries.append(e)

    def update():
        cursor.execute("""
        UPDATE books
        SET title=?, author=?, category=?
        WHERE id=?
        """, (
            entries[1].get(),
            entries[2].get(),
            entries[3].get(),
            entries[0].get()
        ))
        conn.commit()
        messagebox.showinfo("Success", "Book Updated")
        win.destroy()

    tk.Button(win, text="Update", command=update).grid(row=5, columnspan=2)

# ==========================================================
# MEMBERSHIP MANAGEMENT
# ==========================================================

def add_membership_window():
    win = tk.Toplevel(root)
    win.title("Add Membership")

    tk.Label(win, text="Member Name").grid(row=0, column=0)
    tk.Label(win, text="Duration").grid(row=1, column=0)

    name = tk.Entry(win)
    duration = tk.Entry(win)

    name.grid(row=0, column=1)
    duration.grid(row=1, column=1)

    def save():
        if not name.get().strip() or not duration.get().strip():
            messagebox.showerror("Error", "All fields required")
            return

        cursor.execute("""
        INSERT INTO members(name,duration)
        VALUES(?,?)
        """, (name.get(), duration.get()))
        conn.commit()
        messagebox.showinfo("Success", "Membership Added")
        win.destroy()

    tk.Button(win, text="Save", command=save).grid(row=2, columnspan=2)

# ----------------------------------------------------------

def update_membership_window():
    win = tk.Toplevel(root)
    win.title("Update Membership")

    tk.Label(win, text="Member ID").grid(row=0, column=0)
    tk.Label(win, text="New Duration").grid(row=1, column=0)

    mid = tk.Entry(win)
    dur = tk.Entry(win)

    mid.grid(row=0, column=1)
    dur.grid(row=1, column=1)

    def update():
        cursor.execute("""
        SELECT * FROM members WHERE id=?
        """, (mid.get(),))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Invalid Member ID")
            return

        cursor.execute("""
        UPDATE members SET duration=? WHERE id=?
        """, (dur.get(), mid.get()))
        conn.commit()
        messagebox.showinfo("Success", "Membership Updated")
        win.destroy()

    tk.Button(win, text="Update", command=update).grid(row=2, columnspan=2)

# ----------------------------------------------------------

def cancel_membership_window():
    win = tk.Toplevel(root)
    win.title("Cancel Membership")

    tk.Label(win, text="Member ID").grid(row=0, column=0)
    mid = tk.Entry(win)
    mid.grid(row=0, column=1)

    def cancel():
        cursor.execute("""
        SELECT * FROM members WHERE id=?
        """, (mid.get(),))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Invalid Member ID")
            return

        cursor.execute("""
        UPDATE members SET active=0 WHERE id=?
        """, (mid.get(),))
        conn.commit()
        messagebox.showinfo("Success", "Membership Cancelled")
        win.destroy()

    tk.Button(win, text="Cancel Membership", command=cancel).grid(row=1, columnspan=2)

# ==========================================================
# USER MANAGEMENT
# ==========================================================

def user_management_window():
    win = tk.Toplevel(root)
    win.title("User Management")

    labels = ["Username", "Password", "Role"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0)

        if label == "Role":
            e = ttk.Combobox(win, values=["admin", "user"])
        else:
            e = tk.Entry(win)

        e.grid(row=i, column=1)
        entries.append(e)

    # Add User
    def add_user():
        try:
            cursor.execute("""
            INSERT INTO users VALUES(?,?,?)
            """, (
                entries[0].get(),
                entries[1].get(),
                entries[2].get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "User Added")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    # Update User
    def update_user():
        cursor.execute("""
        SELECT * FROM users WHERE username=?
        """, (entries[0].get(),))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Username not found")
            return

        cursor.execute("""
        UPDATE users SET password=?, role=? WHERE username=?
        """, (
            entries[1].get(),
            entries[2].get(),
            entries[0].get()
        ))
        conn.commit()
        messagebox.showinfo("Success", "User Updated")

    # Delete User
    def delete_user():
        cursor.execute("""
        SELECT * FROM users WHERE username=?
        """, (entries[0].get(),))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Username not found")
            return

        cursor.execute("""
        DELETE FROM users WHERE username=?
        """, (entries[0].get(),))
        conn.commit()
        messagebox.showinfo("Success", "User Deleted")

    tk.Button(win, text="Add", command=add_user).grid(row=4, column=0)
    tk.Button(win, text="Update", command=update_user).grid(row=4, column=1)
    tk.Button(win, text="Delete", command=delete_user).grid(row=5, columnspan=2)

# ==========================================================
# SEARCH BOOKS
# ==========================================================

def search_books_window():
    win = tk.Toplevel(root)
    win.title("Search Books")

    tk.Label(win, text="Enter Title or Author").pack(pady=10)

    keyword = tk.Entry(win, width=40)
    keyword.pack()

    result = tk.Text(win, width=70, height=20)
    result.pack(pady=10)

    def search():
        if not keyword.get().strip():
            messagebox.showerror("Error", "At least one search field required")
            return

        result.delete("1.0", tk.END)

        cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
        """, (
            '%' + keyword.get() + '%',
            '%' + keyword.get() + '%'
        ))

        rows = cursor.fetchall()

        if not rows:
            result.insert(tk.END, "No matching books found.")
        else:
            for row in rows:
                result.insert(tk.END, str(row) + "\n")

    tk.Button(win, text="Search", command=search).pack()

# ==========================================================
# ISSUE BOOK MODULE
# ==========================================================

def issue_book_window():
    win = tk.Toplevel(root)
    win.title("Issue Book")
    win.geometry("450x280")

    tk.Label(win, text="Book Name").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(win, text="Member ID").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(win, text="Author").grid(row=2, column=0, padx=10, pady=5)
    tk.Label(win, text="Return Date (YYYY-MM-DD)").grid(row=3, column=0, padx=10, pady=5)

    book_name = tk.Entry(win, width=25)
    member_id = tk.Entry(win, width=25)

    author_var = tk.StringVar()
    author_entry = tk.Entry(win, textvariable=author_var, state="readonly", width=25)

    return_entry = tk.Entry(win, width=25)
    default_return = str(datetime.today().date() + timedelta(days=15))
    return_entry.insert(0, default_return)

    book_name.grid(row=0, column=1)
    member_id.grid(row=1, column=1)
    author_entry.grid(row=2, column=1)
    return_entry.grid(row=3, column=1)

    # Auto-fill author
    def autofill(event=None):
        cursor.execute("""
        SELECT id, author, available FROM books WHERE title=?
        """, (book_name.get(),))
        row = cursor.fetchone()
        if row:
            author_var.set(row[1])
        else:
            author_var.set("")

    book_name.bind("<FocusOut>", autofill)

    # Issue Book Logic
    def issue():
        # Validate member
        cursor.execute("""
        SELECT * FROM members WHERE id=? AND active=1
        """, (member_id.get(),))
        member = cursor.fetchone()

        if not member:
            messagebox.showerror("Error", "Invalid or inactive Member ID")
            return

        # Validate book
        cursor.execute("""
        SELECT id, available FROM books WHERE title=?
        """, (book_name.get(),))
        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "Book not found")
            return

        if row[1] == 0:
            messagebox.showerror("Error", "Book already issued")
            return

        issue_date = datetime.today().date()

        # Validate return date
        try:
            return_date = datetime.strptime(
                return_entry.get(), "%Y-%m-%d"
            ).date()
        except:
            messagebox.showerror("Error", "Invalid date format")
            return

        if return_date > issue_date + timedelta(days=15):
            messagebox.showerror("Error", "Return date cannot exceed 15 days")
            return

        # Insert issue record
        cursor.execute("""
        INSERT INTO issues(book_id,member_id,issue_date,return_date)
        VALUES(?,?,?,?)
        """, (
            row[0],
            member_id.get(),
            str(issue_date),
            str(return_date)
        ))

        # Update availability
        cursor.execute("""
        UPDATE books SET available=0 WHERE id=?
        """, (row[0],))

        # Issue request log
        cursor.execute("""
        INSERT INTO issue_requests(book_id,member_id,status)
        VALUES(?,?,?)
        """, (
            row[0],
            member_id.get(),
            "Issued"
        ))

        conn.commit()
        messagebox.showinfo("Success", "Book Issued Successfully")
        win.destroy()

    tk.Button(win, text="Issue Book", command=issue).grid(row=4, columnspan=2, pady=20)

# ==========================================================
# return book
# ==========================================================

def return_book_window():
    win = tk.Toplevel(root)
    win.title("Return Book")
    win.geometry("450x250")

    tk.Label(win, text="Serial Number").grid(row=0, column=0, padx=10, pady=5)
    serial_entry = tk.Entry(win, width=25)
    serial_entry.grid(row=0, column=1)

    # Auto-display fields
    tk.Label(win, text="Book Name").grid(row=1, column=0, padx=10, pady=5)
    book_var = tk.StringVar()
    book_entry = tk.Entry(win, textvariable=book_var, state="readonly", width=25)
    book_entry.grid(row=1, column=1)

    tk.Label(win, text="Author").grid(row=2, column=0, padx=10, pady=5)
    author_var = tk.StringVar()
    author_entry = tk.Entry(win, textvariable=author_var, state="readonly", width=25)
    author_entry.grid(row=2, column=1)

    tk.Label(win, text="Issue Date").grid(row=3, column=0, padx=10, pady=5)
    issue_var = tk.StringVar()
    issue_entry = tk.Entry(win, textvariable=issue_var, state="readonly", width=25)
    issue_entry.grid(row=3, column=1)

    # ------------------------------------------------------
    # Load Details
    # ------------------------------------------------------
    def load_details():
        cursor.execute("""
        SELECT books.id, books.title, books.author, issues.issue_date, issues.return_date
        FROM issues
        JOIN books ON issues.book_id = books.id
        WHERE issues.serial_no=? AND issues.returned=0
        """, (serial_entry.get(),))

        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "Invalid Serial Number")
            return

        book_var.set(row[1])
        author_var.set(row[2])
        issue_var.set(row[3])

    # ------------------------------------------------------
    # Return Book
    # ------------------------------------------------------
    def return_book():
        cursor.execute("""
        SELECT book_id, return_date
        FROM issues
        WHERE serial_no=? AND returned=0
        """, (serial_entry.get(),))

        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "Invalid Serial Number")
            return

        book_id = row[0]
        due = datetime.strptime(row[1], "%Y-%m-%d").date()
        today = datetime.today().date()

        fine = max((today - due).days, 0) * 5

        cursor.execute("""
        UPDATE issues
        SET returned=1, fine_amount=?
        WHERE serial_no=?
        """, (fine, serial_entry.get()))

        cursor.execute("""
        UPDATE books SET available=1 WHERE id=?
        """, (book_id,))

        conn.commit()

        messagebox.showinfo(
            "Returned",
            f"Returned Successfully\nFine = ₹{fine}"
        )

        win.destroy()

    # Buttons
    tk.Button(
        win,
        text="Load Details",
        command=load_details
    ).grid(row=4, column=0, pady=20)

    tk.Button(
        win,
        text="Return Book",
        command=return_book
    ).grid(row=4, column=1, pady=20)
# ==========================================================
# FINE PAYMENT MODULE
# ==========================================================

def fine_payment_window():
    win = tk.Toplevel(root)
    win.title("Fine Payment")

    tk.Label(win, text="Serial Number").grid(row=0, column=0)
    serial = tk.Entry(win)
    serial.grid(row=0, column=1)

    def pay():
        cursor.execute("""
        SELECT fine_amount, fine_paid FROM issues WHERE serial_no=?
        """, (serial.get(),))
        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "Invalid Serial Number")
            return

        if row[1] == 1:
            messagebox.showinfo("Info", "Fine already paid")
            return

        fine = row[0]

        cursor.execute("""
        INSERT INTO fine_payments(serial_no, amount, payment_date)
        VALUES(?,?,?)
        """, (
            serial.get(),
            fine,
            str(datetime.today().date())
        ))

        cursor.execute("""
        UPDATE issues SET fine_paid=1 WHERE serial_no=?
        """, (serial.get(),))

        conn.commit()
        messagebox.showinfo("Success", f"Fine Paid ₹{fine}")
        win.destroy()

    tk.Button(win, text="Pay Fine", command=pay).grid(row=1, columnspan=2)

# ==========================================================
# REPORTS MODULE
# ==========================================================

def reports_window():
    win = tk.Toplevel(root)
    win.title("Reports")

    text = tk.Text(win, width=90, height=30)
    text.pack()

    def run_report(query):
        text.delete("1.0", tk.END)
        cursor.execute(query)
        for row in cursor.fetchall():
            text.insert(tk.END, str(row) + "\n")

    tk.Button(
        win,
        text="Books Report",
        command=lambda: run_report(
            "SELECT * FROM books WHERE category='Book'"
        )
    ).pack()

    tk.Button(
        win,
        text="Movies Report",
        command=lambda: run_report(
            "SELECT * FROM books WHERE category='Movie'"
        )
    ).pack()

    tk.Button(
        win,
        text="Membership Report",
        command=lambda: run_report(
            "SELECT * FROM members"
        )
    ).pack()

    tk.Button(
        win,
        text="Active Issues",
        command=lambda: run_report(
            "SELECT * FROM issues WHERE returned=0"
        )
    ).pack()

    tk.Button(
        win,
        text="Overdue Returns",
        command=lambda: run_report(
            f"SELECT * FROM issues WHERE returned=0 AND return_date<'{datetime.today().date()}'"
        )
    ).pack()

    tk.Button(
        win,
        text="Issue Requests",
        command=lambda: run_report(
            "SELECT * FROM issue_requests"
        )
    ).pack()
show_login_screen()
root.mainloop()
