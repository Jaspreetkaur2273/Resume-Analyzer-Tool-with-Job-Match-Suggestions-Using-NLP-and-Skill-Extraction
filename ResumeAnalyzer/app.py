from flask import Flask, render_template, request # type: ignore
import os
import re
import PyPDF2 # type: ignore

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Predefined Job Roles and Required Skills
JOB_ROLES = {
    "Data Scientist": ["python", "machine learning", "statistics", "pandas", "numpy", "data visualization"],
    "Web Developer": ["html", "css", "javascript", "react", "bootstrap", "nodejs"],
    "AI Engineer": ["python", "deep learning", "tensorflow", "keras", "neural networks", "nlp"],
    "Software Tester": ["selenium", "automation", "java", "test cases", "jira", "bug tracking"],
    "Database Administrator": ["sql", "mysql", "database", "data backup", "normalization", "oracle"]
}

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    # Define a simple skill list to match against
    common_skills = [
        "python", "java", "c++", "html", "css", "javascript", "react", "sql",
        "machine learning", "deep learning", "nlp", "tensorflow", "keras",
        "pandas", "numpy", "data analysis", "ai", "bootstrap", "django", "flask"
    ]
    found = [skill for skill in common_skills if re.search(r'\b' + re.escape(skill) + r'\b', text)]
    return found

def extract_certificates(text):
    pattern = r"(certificate|certified|certification|course)\s+in\s+[A-Za-z ]+"
    return re.findall(pattern, text, re.IGNORECASE)

@app.route('/')
def home():
    return render_template('index.html', job_roles=JOB_ROLES.keys())

@app.route('/upload', methods=['POST'])
def upload_file():
    job_role = request.form.get('job_role')
    file = request.files.get('resume')

    if not file or file.filename == '':
        return render_template('index.html', job_roles=JOB_ROLES.keys(), result_data={"error": "Please upload a valid PDF."})

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    extracted_skills = extract_skills(text)
    certificates = extract_certificates(text)

    required_skills = JOB_ROLES.get(job_role, [])
    matched_skills = [s for s in extracted_skills if s in required_skills]
    missing_skills = [s for s in required_skills if s not in extracted_skills]

    # Calculate score
    score = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0

    result_data = {
        "job_role": job_role,
        "filename": file.filename,
        "word_count": len(text.split()),
        "extracted_skills": extracted_skills,
        "certificates": certificates,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "score": score
    }

    return render_template('index.html', job_roles=JOB_ROLES.keys(), result_data=result_data)

if __name__ == '__main__':
    app.run(debug=True)
