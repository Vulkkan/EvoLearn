import os
from gtts import gTTS
import PyPDF2


def extract_text_from_file(file_path: str) -> str:
    """
    Extracts and returns text content from a file (either .txt or .pdf).

    Parameters:
    ----------
    file_path : str
        The full path to the file to extract text from. Supported formats: .txt and .pdf

    Returns:
    -------
    str
        The extracted text content from the file.

    Raises:
    ------
    ValueError
        If the file format is not supported (i.e., not .txt or .pdf).
    """

    # If the file is a plain text file, read and return the text content
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # If the file is a PDF, use PyPDF2 to extract text from all pages
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                # Extract text from each page and concatenate
                text += page.extract_text() or ""
            return text

    # Raise an error for unsupported file types
    else:
        raise ValueError("Unsupported file format. Use .txt or .pdf")



def generate_audio_gtts(input: str, output_path: str):
    tts = gTTS(
        text=input,
        lang="en", 
        slow=False, 
        tld="com.ng"
)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tts.save(output_path)
    print(f"✅ Audio note saved to {output_path}")


def main():
    input_dir = "input/materials"
    output_dir = "output/audio"

    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' does not exist.")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(".txt") or f.endswith(".pdf")]

    if not files:
        print("📭 No .txt or .pdf files found in input directory.")
        return

    for file in files:
        file_path = os.path.join(input_dir, file)
        print(f"🔍 Processing {file_path}...")

        try:
            text = extract_text_from_file(file_path).strip()

            if not text:
                print(f"⚠️ No extractable text found in '{file}'")
                continue

            base_name = os.path.splitext(file)[0]
            output_path = os.path.join(output_dir, f"{base_name}.mp3")

            generate_audio_gtts(text, output_path)

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()
