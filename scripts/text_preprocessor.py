import pdfplumber
import fitz  # PyMuPDF
import os
import string
import re
import unicodedata
from num2words import num2words


def get_non_bold_lines(pdf_path):
    """
    Identify non-bold lines on the first page of a PDF.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: A list of non-bold lines (text) from the first page.
    """
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:  
            return []
        
        first_page = pdf.pages[0]  # Get the first page
        chars = first_page.chars
        lines = {}                 # Dictionary to group characters by their y-coordinate (line)

        # Group characters by their vertical position (y-coordinate)
        for char in chars:
            line_y = round(char["top"], 1)  
            if line_y not in lines:
                lines[line_y] = []
            lines[line_y].append(char)

        non_bold_lines = []

        # Check each line and collect non-bold lines
        for line_chars in lines.values():
            if not any("Bold" in char["fontname"] for char in line_chars):
                line_text = "".join(char["text"] for char in line_chars).strip()
                if line_text:  # Exclude empty lines
                    non_bold_lines.append(line_text)

        return non_bold_lines


def extract_text(pdf_path):
    """
    Extract text from a PDF, excluding bold lines from the first page.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Extracted text from the PDF, excluding bold lines from the first page.
    """
    # Get non-bold lines from the first page using pdfplumber
    non_bold_lines_first_page = get_non_bold_lines(pdf_path)

    # Open the PDF document using PyMuPDF
    doc = fitz.open(pdf_path)
    text = []

    # Iterate over each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  
        blocks = page.get_text("dict")["blocks"]  
        page_lines = []

        for block in blocks:
            for line in block.get("lines", []):
                line_text = "".join([span.get("text", "") for span in line.get("spans", [])]).strip()

                # Exclude bold lines on the first page
                if page_num == 0 and line_text not in non_bold_lines_first_page:
                    continue

                page_lines.append(line_text)

        # Add remaining lines to the text output
        if page_lines:
            text.append("\n".join(page_lines))

    # Close the document
    doc.close()

    return "\n".join(text)


def clean_text(raw_text):
    """
    Clean the text by:
    - Replacing "" or "x" in dimensions (e.g., "64  64") with "cross"
    - Removing unwanted patterns like "Refer Slide Time" and timestamps
    - Removing lines starting with "Student:"
    - Converting digits to their spoken form
    - Removing punctuation, including apostrophes
    - Converting to lowercase
    Args:
        raw_text (str): Raw text to process.
    Returns:
        str: Processed text.
    """

    # Replace dimensions like "6464", "FF", "M x N", "1  1  depth"
    raw_text = re.sub(
        r"(\b\w+\b)(\s*[xX]\s*\b\w+\b)+",
        lambda m: " cross ".join(re.split(r"\s*[xX]\s*", m.group(0))),
        raw_text
    )

    # Remove "(Refer Slide Time: xx:xx)" or "(Refer Time: xx:xx)" patterns
    raw_text = re.sub(r"\(Refer (Slide )?Time: \d{2}:\d{2}\)", "", raw_text)

    # Remove lines starting with "Student:"
    raw_text = "\n".join(line for line in raw_text.splitlines() if not line.strip().startswith("Student:"))

    # Convert to lowercase
    raw_text = raw_text.lower()

    # Remove punctuation before digit conversion
    raw_text_no_punctuation = raw_text.translate(str.maketrans("", "", string.punctuation))

    # Convert digits to words
    processed_text = []
    for word in raw_text_no_punctuation.split():
        if word.isdigit():  # Check if the word is numeric
            processed_text.append(num2words(int(word)))  # Convert to words
        else:
            processed_text.append(word)

    # Rejoin text
    text = " ".join(processed_text)

    # Normalize text to handle special Unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove punctuation again to clean any added by num2words
    text = text.translate(str.maketrans("", "", string.punctuation + "’'‘“”"))

    return text


def process_pdfs(input_dir, output_dir):
    """
    Process PDFs to extract text, clean it, and save it as .txt files.
    Args:
        input_dir (str): Directory containing the input PDF files.
        output_dir (str): Directory to save the processed .txt files.
    """
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.txt")

            print(f"Processing: {file_name}")
            
            raw_text = extract_text(pdf_path)
            processed_text = clean_text(raw_text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(processed_text)

    print("Processing complete.")


if __name__ == "__main__":
    input_dir = "./transcripts"
    output_dir = "./preprocessed_text"
    process_pdfs(input_dir, output_dir)
