import io
import fitz  # PyMuPDF for reading PDFs
from transformers import pipeline
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# loadind the pretrained model "facebook - bert model" using HUgging Face taransformers library
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_file):
    # getting the text form the pdf using pymupdf
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def format_summary(summary_text, words_per_line=13):

    # formatting the word count for each line
    words = summary_text.split()
    lines = [' '.join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)]
    return '\n'.join(lines)

def summarize_text(text, target_word_count=300):
    
    # splitting text into chunks and do the summarization using the lodead model
    max_chunk_words = 500
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len((current_chunk + sentence).split()) <= max_chunk_words:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]
        summary += result['summary_text'] + " "

    # Trim the summary to the desired word count
    summary_words = summary.split()
    trimmed_summary = ' '.join(summary_words[:target_word_count])
    return format_summary(trimmed_summary, words_per_line=13)

def generate_note_file(summary_text, format="txt"):

    buffer = io.BytesIO()

    if format == "pdf":
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        for line in summary_text.split('\n'):
            p.drawString(50, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = height - 50
        p.save()
    else:
        buffer.write(summary_text.encode())

    buffer.seek(0)
    return buffer

def analyze_pdf(pdf_file, output_format="txt"):
 
    text = extract_text_from_pdf(pdf_file)
    summary = summarize_text(text, target_word_count=300)
    note_file = generate_note_file(summary, format=output_format)
    return note_file
