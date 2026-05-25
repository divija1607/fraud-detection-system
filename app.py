from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# CREATE DATABASE
conn = sqlite3.connect('fraud.db', check_same_thread=False)
cursor = conn.cursor()

# CREATE TABLES
cursor.execute('''
CREATE TABLE IF NOT EXISTS blacklist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    reason TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS whitelist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    amount REAL,
    status TEXT
)
''')

conn.commit()

# INSERT SAMPLE DATA
cursor.execute("SELECT * FROM blacklist WHERE email='fraud@gmail.com'")
if not cursor.fetchone():
    cursor.execute("""
    INSERT INTO blacklist(name,email,reason)
    VALUES('Fraud User','fraud@gmail.com','Fake Transaction')
    """)

cursor.execute("SELECT * FROM whitelist WHERE email='trusted@gmail.com'")
if not cursor.fetchone():
    cursor.execute("""
    INSERT INTO whitelist(name,email)
    VALUES('Trusted User','trusted@gmail.com')
    """)

conn.commit()

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# CHECK FRAUD
@app.route('/check', methods=['POST'])
def check():

    name = request.form['name']
    email = request.form['email']
    amount = float(request.form['amount'])

    # CHECK BLACKLIST
    cursor.execute(
        "SELECT * FROM blacklist WHERE email=?",
        (email,)
    )

    black = cursor.fetchone()

    if black:
        status = "BLOCKED - BLACKLISTED USER"

    else:
        # CHECK WHITELIST
        cursor.execute(
            "SELECT * FROM whitelist WHERE email=?",
            (email,)
        )

        white = cursor.fetchone()

        if white:
            status = "APPROVED - WHITELISTED USER"

        else:
            if amount > 50000:
                status = "SUSPICIOUS TRANSACTION"

            else:
                status = "NORMAL TRANSACTION"

    # SAVE TRANSACTION
    cursor.execute("""
    INSERT INTO transactions(name,email,amount,status)
    VALUES(?,?,?,?)
    """, (name, email, amount, status))

    conn.commit()

    return render_template(
        'result.html',
        status=status
    )

# RUN APP
if __name__ == '__main__':
    app.run(debug=True)
    