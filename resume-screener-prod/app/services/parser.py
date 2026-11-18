# app/services/parser.py
import pdfplumber
import docx
import magic
import os

#def validate_and_extract_text(file_stream, filename: str) -> str:
#    # Verify actual MIME type to prevent spoofed malicious uploads
#    mime = magic.from_buffer(file_stream.read(2048), mime=True)
#    file_stream.seek(0)

#    if mime == "application/pdf":
#        with pdfplumber.open(file_stream) as pdf:
#            return "\n".join(page.extract_text() or "" for page in pdf.pages)
            
#    elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#        doc = docx.Document(file_stream)
#        return "\n".join(para.text for para in doc.paragraphs)
        
#    else:
#        raise ValueError(f"Unsupported or unsafe file type: {mime}")


def validate_and_extract_text(file_stream, filename: str) -> str:
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext == "pdf":
        with pdfplumber.open(file_stream) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
            
    elif ext == "docx":
        doc = docx.Document(file_stream)
        return "\n".join(para.text for para in doc.paragraphs)
        
    else:
        raise ValueError(f"Unsupported file extension: .{ext}. Please upload a PDF or DOCX file.")