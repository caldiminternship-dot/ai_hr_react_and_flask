import PyPDF2
import docx
import io

def parse_pdf(file) -> str:
    """Extract text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

def parse_docx(file) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error parsing DOCX: {str(e)}"

def parse_resume(uploaded_file) -> str:
    """
    Parse uploaded resume file (PDF or DOCX) and return text content.
    """
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return parse_pdf(uploaded_file)
    elif file_type in ['docx', 'doc']:
        return parse_docx(uploaded_file)
    else:
        # Fallback for text files
        try:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            return stringio.read()
        except Exception as e:
            return f"Error parsing file: {str(e)}"
