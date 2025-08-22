import os
from fastapi import FastAPI, File, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from helper import generate_quiz
from helper.generate_audio_notes import extract_text_from_file, generate_audio_gtts
from helper.generate_more import extract_text, generate_more_text

from werkzeug.utils import secure_filename

from helper.generate_summary import summarize_pdf_to_file
from helper.generate_text import convert_to_wav_mono, transcribe_vosk
import speech_recognition as sr


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads/"
AUDIO_OUTPUT_FOLDER = "static/audio_output"
SUMMARY_OUTPUT_FOLDER = "static/summaries"
TRANSCRIPT_OUTPUT_FOLDER = "static/transcript_output"
QUIZ_OUTPUT_FOLDER = "output/quiz"
ALLOWED_EXTENSIONS = {'pdf'}


# --------------------- ONBOARDING SCREENS --------------------- #
@app.get("/", response_class=HTMLResponse, name='home')
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/onboarding", response_class=HTMLResponse, name='onboarding')
async def onboarding(request: Request):
    return templates.TemplateResponse("onboarding.html", {"request": request})


# --------------------- AUTH SCREENS --------------------- #
@app.get("/login", response_class=HTMLResponse, name='login')
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse, name='signup')
async def signup(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, name='dashboard')
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# --------------------- INNER SCREENS --------------------- #
# Quiz file upload
@app.get("/quiz_upload", response_class=HTMLResponse, name='quiz_upload')
async def quiz_upload(request: Request):
    return templates.TemplateResponse("inner_pages/quiz_pages/upload.html", {"request": request})

# Quiz
@app.get("/quiz", response_class=HTMLResponse, name='quiz')
async def quiz(request: Request, file_path: str = Query(...), num_questions: int = Query(5)):
    # Extract plain text from the PDF at the given path
    text = generate_quiz.extract_pdf_text(file_path)

    # Generate MCQs from the extracted text
    mcqs = generate_quiz.generate_mcqs(text, num_questions=num_questions)

    # Add numbering to each MCQ (1-based index)
    mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]

    # Render the quiz template with required variables
    return templates.TemplateResponse(
        "inner_pages/quiz_pages/quiz.html",
        {
            "request": request,
            "mcqs": mcqs_with_index,
            "enumerate": enumerate,
            "chr": chr
        }
    )

# TTS
@app.get("/text_to_speech", response_class=HTMLResponse, name='text_to_speech')
async def text_to_speech(request: Request):
    return templates.TemplateResponse("inner_pages/transcribe_pages/text_to_speech.html", {"request": request})

# STT / Transcribe
@app.get("/speech_to_text", response_class=HTMLResponse, name='speech_to_text')
async def speech_to_text(request: Request):
    return templates.TemplateResponse("inner_pages/transcribe_pages/speech_to_text.html", {"request": request})

# Summarize
@app.get("/summary_page", response_class=HTMLResponse, name='summary_page')
async def summary_page(request: Request):
    return templates.TemplateResponse("inner_pages/summarize_pages/summary_page.html", {"request": request})

# Expand
@app.get("/expand_page", response_class=HTMLResponse, name='expand_page')
async def expand_page(request: Request):
    return templates.TemplateResponse("inner_pages/expand_pages/expand_page.html", {"request": request})



# ---------------------------------- APIs --------------------------------- #
# --------------------------------------------------------------------------- #

# ------------------ SPEECH TO TEXT HELPER ------------------ #
async def transcribe_google_speech_recognition(wav_path: str, language: str = "en-UK") -> str:
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        
        # Perform transcription using Google's free speech recognition API
        return recognizer.recognize_google(audio_data, language=language)


# ------------- SPEECH TO TEXT <VOSK & SPEECH_RECOGNITION> ------------- #
@app.post("/generate_text", response_class=HTMLResponse)
async def generate_text(request: Request, file: UploadFile = File(...)):
    if not file:
        return templates.TemplateResponse("transcribe_pages/stt_output.html", {"request": request, "error": "No file uploaded."})

    filename = secure_filename(file.filename)
    original_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save uploaded file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with open(original_path, "wb") as f:
        f.write(await file.read())

    # Define output filenames
    base_name = os.path.splitext(filename)[0]
    wav_path = os.path.join(UPLOAD_FOLDER, base_name + "_converted.wav")
    transcript_filename = base_name + "_transcript.txt"
    transcript_path = os.path.join(TRANSCRIPT_OUTPUT_FOLDER, transcript_filename)

    try:
        # Convert audio to WAV mono
        convert_to_wav_mono(original_path, wav_path)

        # Choose online or offline transcription
        use_online = True  # Set to False to use Vosk

        if use_online:
            transcript = transcribe_google_speech_recognition(wav_path, language="en-US")
        else:
            transcript = transcribe_vosk(wav_path).strip()

        if not transcript:
            transcript = "[⚠️ Transcription completed, but no speech detected.]"

        # Save transcript to file
        os.makedirs(TRANSCRIPT_OUTPUT_FOLDER, exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

    except Exception as e:
        print(f"Transcription error: {e}")
        transcript = f"[❌ Error: {e}]"

    return templates.TemplateResponse(
        "transcribe_pages/stt_output.html",
        {
            "request": request,
            "transcript": transcript,
            "transcript_filename": transcript_filename
        }
    )


# --------------------- TEXT TO SPEECH <gTTS> --------------------- #
@app.post('/generate_audio', response_class=HTMLResponse, name='generate_audio')
async def generate_audio(request: Request, file: UploadFile = File(...)):
    if not file:
        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'error': "No file uploaded."
            }
        )

    # Save uploaded file
    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Extract text from file
        text = extract_text_from_file(file_path).strip()

        if not text:
            return templates.TemplateResponse(
                'transcribe_pages/tts_output.html',
                {
                    'request': request,
                    'error': "No extractable text found in the uploaded file."
                }
            )

        # Generate audio
        audio_filename = os.path.splitext(filename)[0] + ".mp3"
        audio_output_path = os.path.join(AUDIO_OUTPUT_FOLDER, audio_filename)
        os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)

        generate_audio_gtts(text, audio_output_path)

        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'audio_filename': audio_filename
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'error': f"An error occurred: {e}"
            }
        )


# --------------------- GENERATE AUDIO --------------------- #
@app.post("/generate_audio", response_class=HTMLResponse)
async def generate_audio(request: Request, file: UploadFile = File(...)):
    if not file:
        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'error': "No file uploaded."
            }
        )

    # Save uploaded file
    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Extract text from file
        text = extract_text_from_file(file_path).strip()

        if not text:
            return templates.TemplateResponse(
                'transcribe_pages/tts_output.html',
                {
                    'request': request,
                    'error': "No extractable text found in the uploaded file."
                }
            )

        # Generate audio file
        os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)
        audio_filename = os.path.splitext(filename)[0] + ".mp3"
        audio_output_path = os.path.join(AUDIO_OUTPUT_FOLDER, audio_filename)

        generate_audio_gtts(text, audio_output_path)

        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'audio_filename': audio_filename
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            'transcribe_pages/tts_output.html',
            {
                'request': request,
                'error': f"An error occurred: {str(e)}"
            }
        )


# --------------------- SUMMARIZER --------------------- #
@app.post("/generate_summary", response_class=HTMLResponse)
async def generate_summary(request: Request, pdf_file: UploadFile = File(...)):
    if not pdf_file.filename.endswith(".pdf"):
        return templates.TemplateResponse(
            'summarize_pages/summarize_output.html',
            {
                'request': request,
                'error': "Only PDF files are supported."
            }
        )

    filename = secure_filename(pdf_file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    input_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(input_path, "wb") as f:
        f.write(await pdf_file.read())

    try:
        summary_text = summarize_pdf_to_file(input_path)  # Your existing function

        base_name = os.path.splitext(filename)[0]
        summary_filename = f"{base_name}_summary.pdf"
        summary_path = os.path.join(SUMMARY_OUTPUT_FOLDER, summary_filename)

        if not os.path.exists(summary_path):
            return templates.TemplateResponse(
                'summarize_pages/summarize_output.html',
                {
                    'request': request,
                    'error': "Summary generation failed."
                }
            )

        return templates.TemplateResponse(
            'summarize_pages/summarize_output.html',
            {
                'request': request,
                'summary': summary_text,
                'summary_filename': summary_filename
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            'summarize_pages/summarize_output.html',
            {
                'request': request,
                'error': str(e),
            }
        )


# --------------------- SMART ENHANCE --------------------- #
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/generate_more", response_class=HTMLResponse)
async def generate_more(request: Request, file: UploadFile = File(...)):
    # Check if filename is empty
    if not file.filename:
        return templates.TemplateResponse(
            'expand_pages/xpand_output.html',
            {'request': request, 'error': "No file selected"}
        )

    # Validate file extension
    if not allowed_file(file.filename):
        return templates.TemplateResponse(
            'expand_pages/expand_output.html',
            {'request': request, 'error': "Invalid file type"}
        )

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        # Process file
        extracted_text = extract_text(filepath)
        expanded_text = generate_more_text(extracted_text)

        return templates.TemplateResponse(
            'expand_pages/expand_output.html',
            {'request': request, 'expanded': expanded_text}
        )

    except Exception as e:
        return templates.TemplateResponse(
            'expand_pages/expand_output.html',
            {'request': request, 'error': str(e)}
        )



## --------------------- QUIZZER --------------------- #
@app.post("/upload_for_quiz")
async def upload_for_quiz(
    request: Request,
    pdf_file: UploadFile = File(...),
    num_questions: int = Form(5)
):
    if not pdf_file.filename.endswith(".pdf"):
        return RedirectResponse(url=request.url.path, status_code=303)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(pdf_file.filename))

    with open(file_path, "wb") as f:
        f.write(await pdf_file.read())

    return RedirectResponse(
        url=f"/quiz?file_path={file_path}&num_questions={num_questions}",
        status_code=303
    )


@app.route('/questions')
async def questions(request: Request):
    file_path = request.args.get('file_path')
    num_questions = int(request.args.get('num_questions', 5))  # Default to 5
    text = generate_quiz.extract_pdf_text(file_path)
    mcqs = generate_quiz.generate_mcqs(text, num_questions=num_questions)
    mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]

    return templates.TemplateResponse(
            'quiz_pages/quiz.html',
            {
                'request': request,
                "mcqs": mcqs_with_index,
                "enumerate": enumerate,
                "chr": chr
            }
        )
    # return render_template('quiz_pages/quiz.html', mcqs=mcqs_with_index, enumerate=enumerate, chr=chr)
