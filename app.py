import os

import openai
import datetime
from docx import Document
from flask import Flask, redirect, render_template, request, url_for, send_file

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        subject = request.form["subject"]
        jurisdiction = request.form["jurisdiction"]
        doctype = request.form["document"]
        party1 = request.form["party1"]
        party2 = request.form["party2"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(doctype, subject, jurisdiction, party1, party2),
            temperature=0.6,
            max_tokens=3896
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    docfile = Document()
    docfile.add_paragraph(result)
    docfile.save("download/string_to_word_doc.docx")
    return render_template("index.html", result=result)

def generate_prompt(doctype, subject, jurisdiction, party1, party2):
    if doctype == "memo":
        return "Write a full and long explanation of the law of {subject} in {jurisdiction} with section headings. Include in-line citations to statutes and case law with pincites".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize())
    elif doctype == "bullets":
        return "Write a bullet point outline explaining the law of {subject} in {jurisdiction}".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize())
    elif doctype == "contract":
        return "Write a {subject} contract with generic party names governed by the law of {jurisdiction} between {party1} and {party2}".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize(), party1=party1.capitalize(), party2=party2.capitalize())
    elif doctype == "claim_letter":
        return "Write a legal claim letter concerning a {subject} violation under {jurisdiction} law from {party1} to {party2}. Include in-line citations to statutes and case law with pincites".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize(), party1=party1.capitalize(), party2=party2.capitalize())

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
