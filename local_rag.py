from src.vectors import ChromaManager
import os
import PyPDF2
import csv
import json
from docx import Document

chroma = ChromaManager()

# Define the directory containing the documents
docs_directory = "documents"

# List to store documents and metadata
some_docs = []
some_metadatas = []

# Supported file types
supported_file_types = [".pdf", ".csv", ".txt", ".json", ".docx", ".md"]


# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# Function to extract text from CSV
def extract_text_from_csv(file_path):
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        text = " ".join([" ".join(row) for row in reader])
    return text


# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = " ".join([paragraph.text for paragraph in doc.paragraphs])
    return text


# Function to extract text from JSON
def extract_text_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        text = json.dumps(data)
    return text


def add_documents():
    # Iterate over files in the specified directory
    for filename in os.listdir(docs_directory):
        file_path = os.path.join(docs_directory, filename)
        file_extension = os.path.splitext(filename)[1].lower()

        # Check if the file is of a supported type
        if file_extension in supported_file_types:
            print(f"Processing {filename}...")
            if file_extension == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif file_extension == ".csv":
                text = extract_text_from_csv(file_path)
            elif file_extension == ".docx":
                text = extract_text_from_docx(file_path)
            elif file_extension == ".json":
                text = extract_text_from_json(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()

            some_docs.append(text)
            some_metadatas.append({"source": filename})

    # Add documents and metadata to ChromaManager
    chroma.add_documents(docs=some_docs, metadatas=some_metadatas)
    print("Documents added to Chroma")


def reset_database():
    print(f"Database resetting. {chroma.count_documents()} documents about to delete.")
    chroma.delete()

    # # Also delete all except the .gitkeep file in the chroma_db directory
    # for filename in os.listdir("chroma_db"):
    #     if filename != ".gitkeep":
    #         os.remove(os.path.join("chroma_db", filename))


# Example usage:
# add_documents()  # To add documents to the database
# reset_database()  # To reset the database


if __name__ == "__main__":
    choices = ["ADD", "RESET"]
    action_index = input(
        "Select the number of the action to perform: \n1. ADD \n2. RESET "
    )
    action = choices[int(action_index) - 1]
    if action == "ADD":
        add_documents()
    elif action == "RESET":
        reset_database()
