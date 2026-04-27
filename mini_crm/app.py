from flask import Flask
from flask import render_template
import sqlite3
from flask import request, redirect

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


''' ******************* DASHBOARD PAGE ******************* '''


@app.route('/')
def dashboard():
    conn = get_db_connection()

    total = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    leads = conn.execute("SELECT COUNT(*) FROM contacts WHERE stage='Lead'").fetchone()[0]
    converted = conn.execute("SELECT COUNT(*) FROM contacts WHERE stage='Converted'").fetchone()[0]
    followups = conn.execute("SELECT COUNT(*) FROM contacts WHERE follow_up IS NOT NULL").fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        leads=leads,
        converted=converted,
        followups=followups
    )


''' *******************  CONTACTS PAGE ******************** '''


@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs ORDER BY date DESC').fetchall()

    # ******************** HANDLE CONTACTSPOST REQUESTS **********************
    if request.method == 'POST':

        # ADD CONTACT
        if 'name' in request.form:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            company = request.form['company']
            follow_up = request.form['follow_up']

            conn.execute(
                'INSERT INTO contacts (name, email, phone, company, follow_up) VALUES (?, ?, ?, ?, ?)',
                (name, email, phone, company, follow_up)
            )

        # DELETE CONTACT
        elif 'delete_id' in request.form:
            contact_id = request.form['delete_id']

            conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
            conn.execute('DELETE FROM logs WHERE contact_id = ?', (contact_id,))

            conn.commit()


        # MOVE CONTACT STAGE
        elif 'contact_id' in request.form and 'stage' in request.form:
            contact_id = request.form['contact_id']
            new_stage = request.form['stage']

            conn.execute(
                'UPDATE contacts SET stage = ? WHERE id = ?',
                (new_stage, contact_id)
            )
            conn.commit()

        # ADD LOG ENTRY
        elif 'log_contact_id' in request.form:
            contact_id = request.form['log_contact_id']
            log_type = request.form['type']
            note = request.form['note']

            conn.execute(
                'INSERT INTO logs (contact_id, type, note, date) VALUES (?, ?, ?, datetime("now"))',
                (contact_id, log_type, note)
            )
            conn.commit()

        conn.close()
        return redirect('/contacts')

    # ******************** HANDLE CONTACTS GET REQUEST ********************

    search = request.args.get('search')

    # PIPELINE DATA (WITH SEARCH ONLY ON LEADS)
    if search:
        leads = conn.execute(
            "SELECT * FROM contacts WHERE stage='Lead' AND name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        leads = conn.execute("SELECT * FROM contacts WHERE stage='Lead'").fetchall()

    contacted = conn.execute("SELECT * FROM contacts WHERE stage='Contacted'").fetchall()
    proposal = conn.execute("SELECT * FROM contacts WHERE stage='Proposal Sent'").fetchall()
    converted = conn.execute("SELECT * FROM contacts WHERE stage='Converted'").fetchall()
    due_today = conn.execute("SELECT * FROM contacts WHERE follow_up = date('now')").fetchall()
    overdue = conn.execute("SELECT * FROM contacts WHERE follow_up < date('now')").fetchall()
    all_contacts = conn.execute("SELECT * FROM contacts").fetchall()

    # GET LOGS
    logs = conn.execute('SELECT * FROM logs ORDER BY date DESC').fetchall()

    conn.close()

    return render_template(
        'contacts.html',
        leads=leads,
        contacted=contacted,
        proposal=proposal,
        converted=converted,
        logs=logs,
        due_today=due_today,
        overdue=overdue,
        all_contacts=all_contacts
    )
# ******************* EDIT CONTACT PAGE *******************


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']

        conn.execute(
            'UPDATE contacts SET name=?, email=?, phone=?, company=? WHERE id=?',
            (name, email, phone, company, id)
        )
        conn.commit()
        conn.close()
        return redirect('/contacts')

    contact = conn.execute('SELECT * FROM contacts WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('edit.html', contact=contact)


if __name__ == '__main__':
    app.run(debug=True)