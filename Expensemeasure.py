import sqlite3
import os
import platform
import json
from types import SimpleNamespace
import datetime
import matplotlib
matplotlib.use('Agg')  # Must be called **before** importing pyplot
import matplotlib.pyplot as plt

data = SimpleNamespace(
    date="xxxx-xx-xx",
    time="00:00",
    remaining=0,   
    income=0,
    day="xxx",
    expense=0,
    note="NULL",
    payment="method"
)

db_file = "expense_table.db"
json_file = "user_data.json"  # JSON file for example table data
def user(user_income,user_expense,user_remained):
    global data
    data.income=user_income
    data.expense=user_expense
    data.remaining=user_remained
def transaction(note,payment_method,amount):
    data.remaining-=amount
    data.expense+=amount
    data.payment=payment_method
    data.note=note
def save_db(db_path, category, note, day, amount):
    now = datetime.datetime.now()
    date = data.date if data.date != "xxxx-xx-xx" else now.strftime("%Y-%m-%d")
    time = data.time if data.time != "00:00" else now.strftime("%H:%M:%S")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO details (date, time, category, payment, note, expense, day)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        time,
        category,
        data.payment,
        note,
        amount,  # now correctly mapped to 'expense'
        day
    ))
    conn.commit()
    conn.close()
def save_json():
    # Path to JSON file
    db_folder_path = os.path.join(get_documents_folder(), "db_folder")
    json_path = os.path.join(db_folder_path, json_file)
    json_data = {
        "income": data.income,
        "total_expense": data.expense,
        "remained_balance": data.remaining
    }
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=4)

    print(f"JSON updated at: {json_path}")
def get_documents_folder():
    """Return path to the user's Documents folder"""
    home = os.path.expanduser("~")
    return os.path.join(home, "Documents")

def find_file_system_wide(file_name):
    system = platform.system()
    search_root = "C:\\" if system == "Windows" else "/"
    for root, dirs, files in os.walk(search_root):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

found_path = find_file_system_wide(db_file)

def ready_db_json():
    global db_file, json_file

    # Documents folder path
     
    db_folder_path = os.path.join(get_documents_folder(), "db_folder")
    os.makedirs(db_folder_path, exist_ok=True)
    db_path = os.path.join(db_folder_path, db_file)
    json_path = os.path.join(db_folder_path, json_file)

    # Connect to database
    if found_path:
        print(f"Database exists at: {found_path}")
        conn = sqlite3.connect(found_path)
    else:
        print(f"Database not found, creating new database at {db_path}...")
        conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # Persistent details table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS details(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            category TEXT,
            payment TEXT,
            note TEXT,
            expense FLOAT,
            day TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database ready at: {db_path}")

    # Create JSON file for example data if not exists
    if not os.path.exists(json_path):
        example_data = {
            "income": 0,
            "total_expense": 0,
            "remained_balance": 0
        }
        with open(json_path, "w") as f:
            json.dump(example_data, f, indent=4)
        print(f"JSON file created at: {json_path}")
    else:
        print(f"JSON file already exists at: {json_path}")
    loaddetails_json(json_path,data)
# Standalone function to convert JSON to namespace
def loaddetails_json(json_path, namespace_obj):
    """
    Load JSON data from a file and update the given SimpleNamespace.
    Maps JSON keys to namespace variables.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} does not exist")
    
    with open(json_path, "r") as f:
        json_data = json.load(f)
    
    # Map JSON keys to namespace attributes
    key_mapping = {
        "income": "income",
        "total_expense": "expense",
        "remained_balance": "remaining"
    }

    for json_key, ns_attr in key_mapping.items():
        if json_key in json_data:
            setattr(namespace_obj, ns_attr, json_data[json_key])
def printall(db_path):
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM details")
    rows = cursor.fetchall()
    
    if not rows:
        print("No records found in the database.")
    else:
        print("ID | Date       | Time     | Category | Payment | Note | Expense")
        print("-" * 60)
        for row in rows:
            # row = (id, date, time, category, payment, note, expense)
            print(f"{row[0]:<3} | {row[1]:<10} | {row[2]:<8} | {row[3]:<8} | {row[4]:<7} | {row[5]:<10} | {row[6]:<7}")

    conn.close()
# Inside Expensemeasure.py
def get_all_transactions():
    db_folder_path = os.path.join(get_documents_folder(), "db_folder")
    db_path = os.path.join(db_folder_path, db_file)
    
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM details ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
def manual_update_json(income=None, total_expense=None, remained_balance=None):
    """
    Manually update the JSON file with new values.
    Pass None for any value you don’t want to change.
    """
    db_folder_path = os.path.join(get_documents_folder(), "db_folder")
    os.makedirs(db_folder_path, exist_ok=True)  # make sure folder exists
    json_path = os.path.join(db_folder_path, json_file)

    # Load current data first
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            json_data = json.load(f)
    else:
        json_data = {
            "income": 0,
            "total_expense": 0,
            "remained_balance": 0
        }

    # Update only the provided fields
    if income is not None:
        json_data["income"] = income
    if total_expense is not None:
        json_data["total_expense"] = total_expense
    if remained_balance is not None:
        json_data["remained_balance"] = remained_balance

    # Save it back
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=4)

    # Also update the in-memory namespace
    data.income = json_data["income"]
    data.expense = json_data["total_expense"]
    data.remaining = json_data["remained_balance"]


def graph():
    transactions = get_all_transactions()
    # Initialize all days of the week to 0
    week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    expense_per_day = {day: 0 for day in week_order}

    # Add actual expenses
    for row in transactions:
        day = row[7]  # day column
        expense = row[6]  # expense column
        if not isinstance(expense, (int, float)):
            expense = float(expense) if expense else 0
        if day in expense_per_day:
            expense_per_day[day] += expense
        else:
            expense_per_day[day] = expense

    sorted_days = week_order
    sorted_expenses = [expense_per_day[day] for day in sorted_days]

    # Plot bars
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(sorted_days, sorted_expenses, color='skyblue')
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Expenses")
    ax.set_title("Expenses by Day")
    ax.set_ylim(0, max(sorted_expenses) * 1.2 if sorted_expenses else 1)
    
    # Show value on top of bars
    for i, v in enumerate(sorted_expenses):
        ax.text(i, v + (max(sorted_expenses)*0.02 if sorted_expenses else 0.1), f"{v:.2f}", ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save figure
    db_folder_path = os.path.join(get_documents_folder(), "db_folder")
    os.makedirs(db_folder_path, exist_ok=True)
    graph_path = os.path.join(db_folder_path, "expense_graph.png")
    fig.savefig(graph_path)
    plt.close(fig)
    return graph_path
