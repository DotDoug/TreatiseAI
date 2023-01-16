import os
import math
import openai
import datetime
from docx import Document
from flask import Flask, redirect, render_template, request, url_for, send_file, request
import treatise_engine as tr

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route("/", methods=("GET", "POST"))
def index():
    user = {'username': 'User1'}
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
    return send_file(file_path, as_attachment=True, attachment_filename=download_name)
