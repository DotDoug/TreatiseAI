import os
import openai
import datetime
import sqlite3
from docx import Document
from flask import Flask, redirect, render_template, request, url_for, send_file, request, session
import treatise_engine as tr
import uuid
import json

app = Flask(__name__)
app.secret_key = os.getenv("COOKIE_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the SQLite database
conn = sqlite3.connect('/home/treatiseai/TreatiseAI/user_credentials.db', check_same_thread=False)
c = conn.cursor()

# Create the users table if it doesn't already exist
c.execute("""CREATE TABLE IF NOT EXISTS user_credentials (
                username text PRIMARY KEY,
                password text NOT NULL
            );""")
conn.commit()

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Check if the user exists in the database
        c.execute("SELECT * FROM user_credentials WHERE username=? AND password=?",
                  (request.form['username'], request.form['password']))
        user = c.fetchone()
        if user is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            # Store the user's username in a session
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route("/", methods=['GET', 'POST'])
def index():
    # Redirect to the login page if the user is not logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    user = {'username': session['username']}
    if request.method == "POST":
        subject = request.form["subject"]
        jurisdiction = request.form["jurisdiction"]
        doctype = request.form["document"]
        response = tr.generate_document(doctype, subject, jurisdiction)
        # Generate a unique ID for the data and store it in a database or file
        data_id = str(uuid.uuid4())
        # Store the data ID in the session cookie
        session['data_id'] = data_id
        # Store the data in a database or file with the data ID as the key
        data = {'response': response}
        if not os.path.exists("/home/treatiseai/TreatiseAI/data/"):
            os.makedirs("/home/treatiseai/TreatiseAI/data/")
        with open(f"/home/treatiseai/TreatiseAI/data/{data_id}.json", "w") as f:
            json.dump(data, f)
        return redirect(url_for("index"))
    # Retrieve the data ID from the session cookie
    data_id = session.get("data_id")
    if data_id:
        # Retrieve the data from the database or file using the data ID
        with open(f"/home/treatiseai/TreatiseAI/data/{data_id}.json", "r") as f:
            data = json.load(f)
        result = data.get("response", "")
    else:
        result = ""
    docfile = Document()
    docfile.add_paragraph(result)
    folder_path = "download"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    docfile.save("TreatiseAI/download/string_to_word_doc.docx")
    return render_template("index.html", user=user, result=result, data_id=data_id)

# Route for handling the logout logic
@app.route('/logout')
def logout():
    # Remove the username from the session
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    error = None
    if request.method == 'POST':
        # Set the row_factory to use dictionaries
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Fetch the current user from the database
        c.execute("SELECT * FROM user_credentials WHERE username=?", (session['username'],))
        user = c.fetchone()

        # Check if the current password is correct
        if user is None or user['password'] != request.form['current_password']:
            error = 'Invalid Current Password. Please try again.'
        else:
            # Update the password in the database
            c.execute("UPDATE user_credentials SET password=? WHERE username=?",
                      (request.form['new_password'], session['username']))
            conn.commit()

            # Redirect the user to the login page
            return redirect(url_for('login'))

    return render_template('change_password.html', error=error)


@app.route('/download')
def download_word_doc():
    # Set the file name and location
    timestamp = datetime.datetime.now()
    timestamp_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    file_name = "string_to_word_doc.docx"
    download_name = "TreatiseAI {time_stamp}.docx".format(time_stamp=timestamp_str)
    file_path = "download/" + file_name

    # Use the send_file function to send the file to the user
    return send_file(file_path, as_attachment=True, download_name=download_name)
