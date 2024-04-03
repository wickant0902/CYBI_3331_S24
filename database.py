import sqlite3
from datetime import datetime

def connect_db():
    """Create a database connection and return the connection object."""
    return sqlite3.connect('expenses.db')

def create_tables():
    """Create the tables needed for the expense tracker."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.executescript('''
        PRAGMA foreign_keys = OFF;
        
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_id INTEGER,
            amount REAL NOT NULL,
            expense_date DATE NOT NULL,
            description TEXT,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        PRAGMA foreign_keys = ON;
        ''')
        conn.commit()

def add_user(username, password):
    """Add a new user to the users table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

def check_user(username, password):
    """Check if a user exists and the password is correct."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
        return cur.fetchone()

def add_category(name):
    """Add a new category to the categories table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()

def get_categories():
    """Retrieve all categories from the categories table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name FROM categories')
        return cur.fetchall()

def add_expense(user_id, category_id, amount, expense_date, description):
    """Add a new expense to the expenses table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO expenses (user_id, category_id, amount, expense_date, description, last_modified)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, category_id, amount, expense_date, description))
        conn.commit()

def get_expenses():
    """Retrieve all expenses for the combined report."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT e.id, e.amount, e.expense_date, c.name AS category_name, u.username, e.description, e.last_modified
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        JOIN users u ON e.user_id = u.id
        ORDER BY e.expense_date DESC
        ''')
        return cur.fetchall()

def get_user_expenses(user_id, period=None):
    """Retrieve expenses for a given user based on a time period."""
    query = '''
    SELECT e.id, e.amount, e.expense_date, c.name AS category_name, e.description, e.last_modified
    FROM expenses e
    JOIN categories c ON e.category_id = c.id
    WHERE e.user_id = ?
    '''
    params = [user_id]

    if period == 'daily':
        query += " AND e.expense_date = date('now')"
    elif period == 'weekly':
        query += " AND e.expense_date >= date('now', '-7 days')"
    elif period == 'monthly':
        query += " AND e.expense_date >= date('now', 'start of month')"
    elif period == 'yearly':
        query += " AND e.expense_date >= date('now', 'start of year')"

    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

def update_expense(expense_id, amount, expense_date, description):
    """Update an existing expense with new values."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''
        UPDATE expenses
        SET amount = ?, expense_date = ?, description = ?, last_modified = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (amount, expense_date, description, expense_id))
        conn.commit()

def delete_expense(expense_id):
    """Delete an expense from the expenses table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()

def update_category(category_id, new_name):
    """Update the name of an existing category."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
        conn.commit()

def delete_category(category_id):
    """Delete a category from the categories table."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()

def category_has_expenses(category_id):
    """Check if a category has linked expenses."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM expenses WHERE category_id = ?', (category_id,))
        return cur.fetchone()[0] > 0

if __name__ == '__main__':
    create_tables()
