import os
import math
import openai
import datetime
import sqlite3
from docx import Document
from flask import Flask, redirect, render_template, request, url_for, send_file, request, session
import treatise_engine as tr

app = Flask(__name__)
app.secret_key = os.getenv("COOKIE_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the SQLite database
conn = sqlite3.connect('user_credentials.db', check_same_thread=False)
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

@app.route("/", methods=("GET", "POST"))
def index():
    # Redirect to the login page if the user is not logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    user = {'username': session['username']}
    if request.method == "POST":
        subject = request.form["subject"]
        jurisdiction = request.form["jurisdiction"]
        doctype = request.form["document"]
        party1 = request.form["party1"]
        party2 = request.form["party2"]
        response = tr.generate_document(doctype, subject, jurisdiction, party1, party2)
        return redirect(url_for("index", result=response))
    result = request.args.get("result")
    docfile = Document()
    docfile.add_paragraph(result)
    folder_path = "download"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    docfile.save("download/string_to_word_doc.docx")
    return render_template("index.html", user=user, result=result)

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
