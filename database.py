import sqlite3
import bcrypt

# Name of the database file
DATABASE_NAME = "expenses.db"

# Function to connect to the database
def connect_db():
    return sqlite3.connect(DATABASE_NAME)

# Function to create database tables if they don't exist
def create_tables():
    with connect_db() as conn:
        # Create 'users' table to store user information
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        # Create 'categories' table to store expense categories
        conn.execute('''CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL)''')
        # Create 'expenses' table to store user expenses
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        category_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        expense_date TEXT NOT NULL,
                        description TEXT,
                        last_modified TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(category_id) REFERENCES categories(id))''')

# Function to add a new user to the database
def add_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with connect_db() as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        return True
    except sqlite3.IntegrityError:
        return False

# Function to check user credentials during login
def check_user(username, password):
    with connect_db() as conn:
        user = conn.execute("SELECT id, password FROM users WHERE username = ?", (username,)).fetchone()
        if user and bcrypt.checkpw(password.encode(), user[1]):
            return user[0]
    return None

# Function to add a new expense category
def add_category(name):
    try:
        with connect_db() as conn:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        return True
    except sqlite3.IntegrityError:
        return False

# Function to retrieve all expense categories
def get_categories():
    with connect_db() as conn:
        return conn.execute("SELECT id, name FROM categories").fetchall()

# Function to add a new expense record
def add_expense(user_id, category_id, amount, expense_date, description):
    with connect_db() as conn:
        conn.execute('''INSERT INTO expenses (user_id, category_id, amount, expense_date, description)
                        VALUES (?, ?, ?, ?, ?)''', (user_id, category_id, amount, expense_date, description))

# Function to retrieve all expenses
def get_expenses():
    with connect_db() as conn:
        return conn.execute('''SELECT e.id, e.expense_date, e.amount, u.username, c.name, e.description, e.last_modified
                               FROM expenses e
                               JOIN users u ON e.user_id = u.id
                               JOIN categories c ON e.category_id = c.id
                               ORDER BY e.expense_date DESC''').fetchall()

# Function to retrieve expenses for a specific user and period
def get_user_expenses(user_id, period):
    period_sql = {
        "daily": "AND DATE(expense_date) = DATE('now')",
        "weekly": "AND DATE(expense_date) >= DATE('now', '-7 days')",
        "monthly": "AND STRFTIME('%Y-%m', expense_date) = STRFTIME('%Y-%m', 'now')",
        "yearly": "AND STRFTIME('%Y', expense_date) = STRFTIME('%Y', 'now')",
        "all": ""
    }.get(period, "")
    
    sql = '''SELECT e.id, e.expense_date, e.amount, u.username, c.name, e.description, e.last_modified
             FROM expenses e
             JOIN users u ON e.user_id = u.id
             JOIN categories c ON e.category_id = c.id
             WHERE e.user_id = ? {}
             ORDER BY e.expense_date DESC'''.format(period_sql)
    
    with connect_db() as conn:
        return conn.execute(sql, (user_id,)).fetchall()

# Function to update an expense record
def update_expense(expense_id, amount, expense_date, description):
    with connect_db() as conn:
        conn.execute('''UPDATE expenses
                        SET amount = ?, expense_date = ?, description = ?, last_modified = CURRENT_TIMESTAMP
                        WHERE id = ?''', (amount, expense_date, description, expense_id))

# Function to delete an expense record
def delete_expense(expense_id):
    with connect_db() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

# Function to update the name of an expense category
def update_category(category_id, name):
    with connect_db() as conn:
        conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))

# Function to check if an expense category has associated expenses
def category_has_expenses(category_id):
    with connect_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM expenses WHERE category_id = ?", (category_id,)).fetchone()[0]
        return count > 0

# Function to delete an expense category if it has no associated expenses
def delete_category(category_id):
    if not category_has_expenses(category_id):
        with connect_db() as conn:
            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return True
    return False

# If the file is executed directly, create the database tables
if __name__ == "__main__":
    create_tables()