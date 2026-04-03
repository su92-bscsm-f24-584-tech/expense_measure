# app.py
import os
import datetime
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
import Expensemeasure

app = Flask(__name__, static_folder='static')

# Set DB folder and path
DB_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "db_folder")
DB_PATH = os.path.join(DB_FOLDER, "expense_table.db")
os.makedirs(DB_FOLDER, exist_ok=True)

# Ensure database and JSON are ready
Expensemeasure.ready_db_json()

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')


# Add new transaction
@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    note = data.get('note', 'NULL')
    payment = data.get('payment', 'Cash')
    category = data.get('category', 'Other')
    amount = float(data.get('amount', 0))
    day = data.get('day', datetime.datetime.now().strftime("%A"))

    # Update in-memory data
    Expensemeasure.data.payment = payment
    Expensemeasure.data.note = note
    Expensemeasure.data.remaining -= amount
    Expensemeasure.data.expense += amount

    # Save transaction to DB
    Expensemeasure.save_db(DB_PATH, category, note, day, amount)

    # Update JSON file
    Expensemeasure.save_json()

    return jsonify({"status": "success"})


# Get all transactions
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    rows = Expensemeasure.get_all_transactions()
    transactions = [
        {
            "id": row[0],
            "date": row[1],
            "time": row[2],
            "category": row[3],
            "payment": row[4],
            "note": row[5],
            "amount": row[6],
            "day": row[7]
        } for row in rows
    ]
    return jsonify(transactions)


# Update income and recalc remaining
@app.route('/api/update-json', methods=['POST'])
def update_json():
    income = request.json.get('income')

    # Calculate total expense from DB
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(expense) FROM details")
        total_expense = cursor.fetchone()[0] or 0

    remaining = income - total_expense
    Expensemeasure.manual_update_json(
        income=income,
        total_expense=total_expense,
        remained_balance=remaining
    )

    return jsonify({
        "status": "success",
        "message": "DETAILS updated successfully",
        "total_expense": total_expense,
        "remaining": remaining
    })


# Get summary (income, expense, remaining)
@app.route('/api/get-summary', methods=['GET'])
def get_summary():
    json_path = os.path.join(DB_FOLDER, "user_data.json")
    Expensemeasure.loaddetails_json(json_path, Expensemeasure.data)
    return jsonify({
        "income": Expensemeasure.data.income,
        "total_expense": Expensemeasure.data.expense,
        "remaining": Expensemeasure.data.remaining
    })
@app.route('/api/graph', methods=['GET'])
def get_graph():
    path = Expensemeasure.graph()
    if path:
        return send_from_directory(os.path.dirname(path), os.path.basename(path))
    return jsonify({"error": "No transactions to plot."})

@app.route('/api/reset', methods=['POST'])
def reset_all():
    # Clear all transactions from DB
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM details")
        conn.commit()

    # Reset JSON data
    Expensemeasure.manual_update_json(
        income=0,
        total_expense=0,
        remained_balance=0
    )

    return jsonify({"status": "success", "message": "All data has been reset."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
