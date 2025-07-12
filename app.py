
from flask import Flask, render_template, request, redirect, url_for, session
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Mock database for users
users = {}
transactions = []
budget = {}

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'User already exists!'
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return 'Invalid credentials!'
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', transactions=transactions, username=session['username'])
    return redirect(url_for('login'))

# Add Transaction
@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction = {
            'type': request.form['type'],
            'amount': float(request.form['amount']),
            'category': request.form['category'],
            'date': request.form['date'],
            'description': request.form.get('description', '')
        }
        transactions.append(transaction)
        save_transactions_to_csv()
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html')

# Save Transactions to CSV
def save_transactions_to_csv():
    with open('data/transactions.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Amount', 'Category', 'Date', 'Description'])
        for transaction in transactions:
            writer.writerow([transaction['type'], transaction['amount'], transaction['category'], transaction['date'], transaction['description']])

# Balance Sheet
@app.route('/balance_sheet')
def balance_sheet():
    assets = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    liabilities = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
    return render_template('balance_sheet.html', assets=assets, liabilities=liabilities)

# Cash Flow Statement
@app.route('/cash_flow', methods=['GET', 'POST'])
def cash_flow():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        income = sum(t['amount'] for t in transactions if t['type'] == 'Income' and start_date <= datetime.strptime(t['date'], '%Y-%m-%d') <= end_date)
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'Expense' and start_date <= datetime.strptime(t['date'], '%Y-%m-%d') <= end_date)
        net_cash = income - expenses
        return render_template('cash_flow.html', income=income, expenses=expenses, net_cash=net_cash)
    return render_template('cash_flow.html')

# Budget
@app.route('/budget', methods=['GET', 'POST'])
def budget_page():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        budget[category] = amount
        save_budget_to_csv()
        return redirect(url_for('budget_page'))
    return render_template('budget.html', budget=budget)

# Save Budget to CSV
def save_budget_to_csv():
    with open('data/budget.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Amount'])
        for category, amount in budget.items():
            writer.writerow([category, amount])

if __name__ == '__main__':
    app.run(debug=True)
