import os
import math
import openai
#import nltk
#from nltk.tokenize import sent_tokenize
#not using function that uses nltk

def generate_document(doctype, subject, jurisdiction, party1, party2):
    if doctype == "memo":
        return write_memo(subject, jurisdiction)
    elif doctype == "longer_memo":
        #this seems to crash flask because it passes the whole memo in URL
        return write_long_memo(subject, jurisdiction)
    elif doctype == "bullets":
        return write_bullets(subject, jurisdiction)
    elif doctype == "contract":
        return write_contract(subject, jurisdiction, party1, party2)
    #elif doctype == "longer_contract":
        #return elaborate_sentences(write_contract(subject, jurisdiction, party1, party2))
    elif doctype == "claim_letter":
        return write_claim_letter(subject, jurisdiction, party1, party2)

def write_memo(subject, jurisdiction):
    outcompletion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a full and long explanation of the law of {subject} in {jurisdiction} with section headings and citations to statute and case law (with pin cites) in the explanation text".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize()),
        temperature=0.6,
        max_tokens=3896 #EVENTUALLY TO COUNT TOKENS IN COMBINED PROMPT AND PUT MAX WITHOUT -- COULD USE HUGGINGFACE BPE MODEL
    )
    return outcompletion.choices[0].text

#Writes a long memo by first creating an outline and then writing the text
#for each item. Most reliable method so far, but will be repetitive
def write_long_memo(subject, jurisdiction):
    outline = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write an alphanumeric outline of a full and long explanation of the law of {subject} in {jurisdiction}".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize()),
        temperature=0.5,
        max_tokens=3896
    )
    outline_string = outline.choices[0].text
    print(outline_string)
    outline_items = extract_outline_items(outline_string)
    enriched_memo_list = []
    for item in outline_items:
        item_text = write_outline_item(item, subject, jurisdiction)
        enriched_memo_list.append(item_text)
    return " ".join(enriched_memo_list)

# Extracts the items from a memo outline
def extract_outline_items(outline):
    items = []
    lines = outline.strip().split("\n")
    for line in lines:
        item = line.strip()
        items.append(item)
    return items

# Takes an item from the outline for a memo and writes the text for it
def write_outline_item(item, subject, jurisdiction):
    outcompletion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write the text for a section called \"{item}\" of a full and long explanation of the law of {subject} in {jurisdiction} citations to statute and case law (with pin cites) in the explanation text".format(item=item, subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize()),
        temperature=0.5,
        max_tokens=3896
    )
    print(item, outcompletion.choices[0].text)
    return outcompletion.choices[0].text

def write_bullets(subject, jurisdiction):
    outcompletion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a bullet point outline explaining the law of {subject} in {jurisdiction}".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize()),
        temperature=0.5,
        max_tokens=3896 #EVENTUALLY TO COUNT TOKENS IN COMBINED PROMPT AND PUT MAX WITHOUT -- COULD USE HUGGINGFACE BPE MODEL
    )
    return outcompletion.choices[0].text

def write_contract(subject, jurisdiction, party1, party2):
    outcompletion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a {subject} contract with generic party names governed by the law of {jurisdiction} between {party1} and {party2}".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize(), party1=party1.capitalize(), party2=party2.capitalize()),
        temperature=0.5,
        max_tokens=3896 #EVENTUALLY TO COUNT TOKENS IN COMBINED PROMPT AND PUT MAX WITHOUT -- COULD USE HUGGINGFACE BPE MODEL
    )
    return outcompletion.choices[0].text

def write_claim_letter(subject, jurisdiction, party1, party2):
    outcompletion = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a legal claim letter concerning a {subject} violation under {jurisdiction} law from {party1} to {party2}. Include in-line citations to statutes and case law with pincites".format(subject=subject.capitalize(), jurisdiction=jurisdiction.capitalize(), party1=party1.capitalize(), party2=party2.capitalize()),
        temperature=0.7,
        max_tokens=3896 #EVENTUALLY TO COUNT TOKENS IN COMBINED PROMPT AND PUT MAX WITHOUT -- COULD USE HUGGINGFACE BPE MODEL
    )
    return outcompletion.choices[0].text

#the below function is unreliable for memos at this time -- adds random legal subjects
#between sentences -- sometimes very lengthy -- and other cases is null or short
#and not particularly helpful
def elaborate_sentences(s):
    sentences = sent_tokenize(s)
    outtext=""
    for i in range(len(sentences)):
        outtext += sentences[i]
        if i < len(sentences) - 1:
            newtext=openai.Completion.create(
                model="text-davinci-003",
                prompt=sentences[i],
                suffix=sentences[i+1],
                temperature=0.7,
                max_tokens=2048
            )
            #below just for test
            print(newtext)
            outtext += newtext.choices[0].text
    return outtext
