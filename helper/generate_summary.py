import os
import fitz  # PyMuPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.lsa import LsaSummarizer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


LANGUAGE = "english"
SENTENCES_COUNT = 500

SUMMARY_OUTPUT_FOLDER = "static/summaries"

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def write_summary_to_pdf(summary_text: str, original_pdf_path: str):
    base_name = os.path.splitext(os.path.basename(original_pdf_path))[0]
    output_path = os.path.join(SUMMARY_OUTPUT_FOLDER, f"{base_name}_summary.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create PDF document with margins (left, right, top, bottom)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        rightMargin=52,  # 1 inch padding on the right
        leftMargin=52,   # 1 inch on the left
        topMargin=52,
        bottomMargin=52
    )

    styles = getSampleStyleSheet()
    story = []

    # Add the summary text (wrapped properly)
    paragraphs = summary_text.split(". ")
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip() + ".", styles["Normal"]))
            story.append(Spacer(1, 12))  # Space between lines

    doc.build(story)
    print(f"✅ Summary saved to: {output_path}")


def summarize_pdf_to_file(pdf_path: str) -> str:
    text = extract_text_from_pdf(pdf_path)
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    summary = " ".join(str(sentence) for sentence in summarizer(parser.document, SENTENCES_COUNT))
    write_summary_to_pdf(summary, pdf_path)

    return summary

# summarize_pdf_to_file("input/materials/EvoLearn.pdf")
