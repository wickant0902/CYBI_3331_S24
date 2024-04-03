import getpass
import database

def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("1. Create an account")
        print("2. Log in")
        print("3. View Combined Expenses Report")
        print("4. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            create_account()
        elif choice == "2":
            user = login()
            if user:
                user_menu(user)
        elif choice == "3":
            view_combined_expenses_without_login()
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

def create_account():
    username = input("Enter a new username: ")
    password = getpass.getpass("Enter a password: ")
    if database.add_user(username, password):
        print("Account created successfully.")
    else:
        print("Account already exists. Please log in.")

def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = database.check_user(username, password)
    if user:
        print("Login successful.")
        return user
    else:
        print("Invalid username or password.")
        return None

def user_menu(user):
    while True:
        print("\n=== User Menu ===")
        print("1. Add Expense")
        print("2. View My Expenses")
        print("3. Manage Categories")
        print("4. Manage My Expenses")
        print("5. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            add_expense(user)
        elif choice == "2":
            view_my_expenses(user)
        elif choice == "3":
            manage_categories()
        elif choice == "4":
            manage_my_expenses(user)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

def add_expense(user):
    categories = database.get_categories()
    if not categories:
        print("No categories found. Please add a category first.")
        return
    print("Select a category for the expense:")
    for idx, (id, name) in enumerate(categories, 1):
        print(f"{idx}. {name}")
    category_choice = int(input("Choice: ")) - 1
    category_id = categories[category_choice][0]

    amount = float(input("Amount: "))
    expense_date = input("Date (YYYY-MM-DD): ")
    description = input("Description: ")
    database.add_expense(user[0], category_id, amount, expense_date, description)
    print("Expense added successfully.")

def view_my_expenses(user):
    print("\n=== View My Expenses ===")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    print("4. Yearly")
    choice = input("Choose period: ")
    expenses = database.get_user_expenses(user[0], choice)
    if expenses:
        print("{:<15} {:<10} {:<15} {:<20} {:<50} {:<20}".format('Date', 'Amount', 'User', 'Category', 'Description', 'Last Modified'))
        print("-" * 135)
        for expense in expenses:
            print("{:<15} {:<10} {:<15} {:<20} {:<50} {:<20}".format(
                expense[2],  # Date
                f"${expense[1]:,.2f}",  # Amount
                user[1],  # User (username)
                expense[3],  # Category Name
                expense[4],  # Description
                expense[5]  # Last Modified
            ))
    else:
        print("No expenses found for this period.")

def manage_categories():
    categories = database.get_categories()
    if not categories:
        print("No categories available.")
        return
    print("\n=== Manage Categories ===")
    print("1. Add Category")
    print("2. Update Category")
    print("3. Delete Category")
    choice = input("Enter choice: ")
    if choice == "1":
        add_category()
    elif choice == "2":
        update_category(categories)
    elif choice == "3":
        delete_category(categories)

def add_category():
    category_name = input("Enter the name of the new category: ")
    database.add_category(category_name)
    print("Category added successfully.")

def update_category(categories):
    for idx, (id, name) in enumerate(categories, 1):
        print(f"{idx}. {name}")
    category_choice = int(input("Select the number of the category to update: ")) - 1
    new_name = input("Enter the new name for the category: ")
    database.update_category(categories[category_choice][0], new_name)
    print("Category updated successfully.")

def delete_category(categories):
    for idx, (id, name) in enumerate(categories, 1):
        print(f"{idx}. {name}")
    category_choice = int(input("Select the number of the category to delete: ")) - 1
    category_id = categories[category_choice][0]
    if database.category_has_expenses(category_id):
        print("Category cannot be deleted because it has linked expenses.")
    else:
        database.delete_category(category_id)
        print("Category deleted successfully.")

def manage_my_expenses(user):
    expenses = database.get_user_expenses(user[0])
    if not expenses:
        print("You have no expenses logged.")
        return
    print("Select the expense you wish to manage:")
    for idx, expense in enumerate(expenses, 1):
        print(f"{idx}. Date: {expense[2]}, Amount: {expense[1]}, Description: {expense[3]}")
    expense_choice = int(input("Enter the number of the expense to manage or 0 to go back: "))
    if expense_choice == 0:
        return
    elif 1 <= expense_choice <= len(expenses):
        selected_expense = expenses[expense_choice - 1]
        print("1. Update Expense")
        print("2. Delete Expense")
        action_choice = input("Enter choice: ")
        if action_choice == "1":
            new_amount = float(input("Enter new amount: "))
            new_date = input("Enter new date (YYYY-MM-DD): ")
            new_description = input("Description: ")
            database.update_expense(selected_expense[0], new_amount, new_date, new_description)
            print("Expense updated successfully.")
        elif action_choice == "2":
            database.delete_expense(selected_expense[0])
            print("Expense deleted successfully.")
    else:
        print("Invalid choice.")

def view_combined_expenses_without_login():
    expenses = database.get_expenses()
    if expenses:
        print("\n=== Combined Expenses Report ===")
        print("{:<15} {:<10} {:<15} {:<20} {:<50} {:<20}".format('Date', 'Amount', 'User', 'Category', 'Description', 'Last Modified'))
        print("-" * 135)
        for expense in expenses:
            print("{:<15} {:<10} {:<15} {:<20} {:<50} {:<20}".format(
                expense[2], 
                f"${expense[1]:,.2f}", 
                expense[4], 
                expense[3], 
                expense[5], 
                expense[6]
            ))
    else:
        print("No expenses have been logged.")

if __name__ == '__main__':
    database.create_tables()
    main_menu()
