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

    # ADD CONTACT
    if request.method == 'POST':
        if 'name' in request.form:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            company = request.form['company']

            conn.execute(
                'INSERT INTO contacts (name, email, phone, company) VALUES (?, ?, ?, ?)',
                (name, email, phone, company)
            )
            conn.commit()

        # MOVE STAGE
        elif 'contact_id' in request.form:
            contact_id = request.form['contact_id']
            new_stage = request.form['stage']

            conn.execute(
                'UPDATE contacts SET stage = ? WHERE id = ?',
                (new_stage, contact_id)
            )
            conn.commit()

        conn.close()
        return redirect('/contacts')

    # GET DATA BY STAGE
    leads = conn.execute("SELECT * FROM contacts WHERE stage='Lead'").fetchall()
    contacted = conn.execute("SELECT * FROM contacts WHERE stage='Contacted'").fetchall()
    proposal = conn.execute("SELECT * FROM contacts WHERE stage='Proposal Sent'").fetchall()
    converted = conn.execute("SELECT * FROM contacts WHERE stage='Converted'").fetchall()

    conn.close()

    return render_template(
        'contacts.html',
        leads=leads,
        contacted=contacted,
        proposal=proposal,
        converted=converted
    )

if __name__ == '__main__':
    app.run(debug=True)
