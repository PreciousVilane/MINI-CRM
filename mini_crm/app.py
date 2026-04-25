from flask import Flask
from flask import render_template
import sqlite3
from flask import request, redirect

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Dashboard page
@app.route('/')
def dashboard():
    return render_template('dashboard.html')


# Contacts page
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    conn = get_db_connection()

    # HANDLE FORM SUBMISSION
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']

        conn.execute(
            'INSERT INTO contacts (name, email, phone, company) VALUES (?, ?, ?, ?)',
            (name, email, phone, company)
        )
        conn.commit()
        conn.close()
        return redirect('/contacts')

    # GET ALL CONTACTS
    contancts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()

    return render_template('contacts.html', contacts=contancts)


if __name__ == '__main__':
    app.run(debug=True)