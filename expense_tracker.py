import getpass
import database
from datetime import datetime

# Function to display the main menu
def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("1. Create an account")
        print("2. Log in")
        print("3. View Combined Expenses Report")
        print("4. Exit Program")
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
            print("Exiting program. Bye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to create a new user account
def create_account():
    username = input("Enter a new username: ")
    password = getpass.getpass("Enter a password: ")
    if database.add_user(username, password):
        print("Account created successfully.")
    else:
        print("Username already taken. Please try another.")

# Function for user login
def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user_id = database.check_user(username, password)
    if user_id:
        print("Login successful.")
        return (user_id, username)
    else:
        print("Login failed. Invalid username or password.")

# Function for user-specific menu options
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

# Function to validate date input
def validate_date_input(message):
    while True:
        date_input = input(message)
        try:
            # Parse date in the format MM-DD-YYYY
            datetime.strptime(date_input, "%m-%d-%Y")
            return date_input
        except ValueError:
            print("Date format incorrect, try again. Use MM-DD-YYYY.") 

# Function to add an expense
def add_expense(user):
    print("=== Add Expense ===")
    categories = database.get_categories()
    if not categories:
        print("No categories found. Please add a category first.")
        return
    print("Select a category for the expense:")
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category[1]}")
    choice = int(input("Choice: ")) - 1
    if choice < 0 or choice >= len(categories):
        print("Invalid choice.")
        return
    category_id = categories[choice][0]
    expense_date = validate_date_input("Date (MM-DD-YYYY): ")
    amount = float(input("Amount: "))
    description = input("Description: ")
    database.add_expense(user[0], category_id, amount, expense_date, description)
    print("Expense added successfully.")

# Function to view user's expenses
def view_my_expenses(user):
    print("=== View My Expenses ===")
    periods = ["Daily", "Weekly", "Monthly", "Yearly"]
    for idx, period in enumerate(periods, start=1):
        print(f"{idx}. {period}")
    choice = input("Choose period: ")
    try:
        period = periods[int(choice) - 1].lower()
    except (ValueError, IndexError):
        print("Invalid choice.")
        return
    expenses = database.get_user_expenses(user[0], period)
    if expenses:
        print_expenses(expenses)
    else:
        print("No expenses found for this period.")

# Function to manage expense categories
def manage_categories():
    print("=== Manage Categories ===")
    print("1. Add Category")
    print("2. Update Category")
    print("3. Delete Category")
    choice = input("Enter choice: ")
    if choice == "1":
        add_category()
    elif choice == "2":
        update_category()
    elif choice == "3":
        delete_category()
    else:
        print("Invalid choice.")

# Function to add a new expense category
def add_category():
    name = input("Enter the name of the new category: ").lower().strip()
    if database.add_category(name):
        print("Category added successfully.")
    else:
        print("This category already exists.")

# Function to update an existing expense category
def update_category():
    print("=== Update Category ===")
    categories = database.get_categories()
    if not categories:
        print("No categories available.")
        return
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category[1]}")
    choice = int(input("Select the category to update: ")) - 1
    if choice < 0 or choice >= len(categories):
        print("Invalid choice.")
        return
    new_name = input("Enter the new name for the category: ").lower().strip()
    database.update_category(categories[choice][0], new_name)
    print("Category updated successfully.")

# Function to delete an existing expense category
def delete_category():
    print("=== Delete Category ===")
    categories = database.get_categories()
    if not categories:
        print("No categories to delete.")
        return
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category[1]}")
    choice = int(input("Select the category to delete: ")) - 1
    if choice < 0 or choice >= len(categories):
        print("Invalid choice.")
        return
    if database.category_has_expenses(categories[choice][0]):
        print("Cannot delete category because it has linked expenses.")
        return
    database.delete_category(categories[choice][0])
    print("Category deleted successfully.")

# Function to manage user's expenses
def manage_my_expenses(user):
    print("=== Manage My Expenses ===")
    expenses = database.get_user_expenses(user[0], "all")
    if not expenses:
        print("No expenses logged.")
        return
    while True:
        for idx, expense in enumerate(expenses, start=1):
            # Format date as MM-DD-YYYY
            try:
                expense_date = datetime.strptime(expense[1], "%Y-%m-%d").strftime("%m-%d-%Y")
            except ValueError:
                expense_date = expense[1]
            print(f"{idx}. Date: {expense_date}, Amount: {expense[2]}, Category: {expense[4]}, Description: {expense[5]}")
        print("0. Go Back")
        choice = input("Select an expense to manage: ")
        if choice == "0":
            return
        try:
            choice = int(choice) - 1
            if choice < 0 or choice >= len(expenses):
                print("Invalid choice.")
                continue
            manage_expense(expenses[choice])
        except ValueError:
            print("Invalid choice. Please enter a number.")

# Function to manage individual expenses
def manage_expense(expense):
    print("1. Update Expense")
    print("2. Delete Expense")
    choice = input("Choice: ")
    if choice == "1":
        update_expense_details(expense)
    elif choice == "2":
        database.delete_expense(expense[0])
        print("Expense deleted successfully.")
    else:
        print("Invalid choice.")

# Function to update details of an expense
def update_expense_details(expense):
    amount = float(input("New amount: "))
    date = validate_date_input("New date (MM-DD-YYYY): ")
    description = input("New description: ")
    database.update_expense(expense[0], amount, date, description)
    print("Expense updated successfully.")

# Function to view combined expenses without logging in
def view_combined_expenses_without_login():
    expenses = database.get_expenses()
    if expenses:
        print_expenses(expenses)
    else:
        print("No expenses have been logged.")

# Function to convert date format if necessary
def convert_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m-%d-%Y")
    except ValueError:
        return date_str

# Function to print expenses
def print_expenses(expenses):
    print(f"{'Date':<15} {'Amount':<10} {'User':<15} {'Category':<20} {'Description':<50} {'Last Modified':<20}")
    user_totals = {}
    category_totals = {}
    
    for expense in expenses:
        try:
            expense_date = convert_date_format(expense[1])

            print(f"{expense_date:<15} ${float(expense[2]):<9.2f} {expense[3]:<15} {expense[4]:<20} {expense[5]:<50} {expense[6]}")
            
            # Calculate user totals
            if expense[3] not in user_totals:
                user_totals[expense[3]] = 0
            user_totals[expense[3]] += float(expense[2])
            
            # Calculate category totals
            if expense[4] not in category_totals:
                category_totals[expense[4]] = 0
            category_totals[expense[4]] += float(expense[2])
            
        except IndexError as e:
            print(f"Error processing expense: {e}")
    
    # Print user totals
    print("\nUser Totals:")
    for user, total in user_totals.items():
        print(f"Total for {user}: ${total:.2f}")
    
    # Print category totals
    print("\nSpending Summary:")
    for category, total in category_totals.items():
        print(f"{category}: ${total:.2f}")

# Main function to start the program
if __name__ == "__main__":
    database.create_tables()
    main_menu()