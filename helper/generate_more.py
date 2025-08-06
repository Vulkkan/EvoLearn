import requests
import json
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TOKEN = os.getenv('OPENROUTER_API_KEY')
MODEL = os.getenv('MODEL')  # default fallback model

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_TOKEN}",
    "Content-Type": "application/json"
}

''' APPROACH
Inputs: PDF file

Operations:
    1. extract information from PDF (questions)
    2. pass information to AI model
    3. get get a much more detailed information and return it

Outputs: text
'''

# 1. Extract text from a PDF file
def extract_text(pdf_path: str) -> str:
    """
    Extracts and returns the full text content from a PDF file using PyMuPDF.

    Parameters:
    ----------
    pdf_path : str
        The path to the PDF file to extract text from.

    Returns:
    -------
    str
        The concatenated text content from all pages of the PDF, with leading and trailing whitespace removed.
    """
    
    # Open the PDF document
    doc = fitz.open(pdf_path)
    
    text = ""
    # Iterate through each page and extract text
    for page in doc:
        text += page.get_text()
    
    # Close the PDF document to free resources
    doc.close()

    # Return the full text with extra whitespace trimmed
    return text.strip()



# 2. Generate more info based on extracted content
def generate_more_text(content: str) -> str:
    prompt = (
        "Below is a brief or incomplete document. Please expand on the ideas, and only work on facts "
        "add explanations, and clarify unclear points while keeping the original intent:\n\n"
        f"{content}\n\n"
        "Expanded version:"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"Error {response.status_code}: {response.text}"
