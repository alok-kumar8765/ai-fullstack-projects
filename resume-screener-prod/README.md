# AI-Powered Enterprise Resume Screening & ATS System 🚀

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Table of Contents
1. [Purpose & Use of This Project](#-purpose--use-of-this-project)
2. [Features](#-features)
3. [File Structure](#-file-structure)
4. [System Architecture & Diagrams](#-system-architecture--diagrams)
   - [Data Flow Diagram (DFD)](#1-data-flow-diagram-dfd)
   - [Entity-Relationship (ER) Diagram](#2-entity-relationship-er-diagram)
5. [Requirements & Prerequisites](#-requirements--prerequisites)
6. [Installation & Setup](#-installation--setup)
7. [Pros & Cons](#-pros--cons)
8. [Limitations](#-limitations)
9. [Known Bugs & Vulnerabilities](#-known-bugs--vulnerabilities)
10. [Future Roadmap & Updates](#-future-roadmap--updates)
11. [Contributing](#-contributing)
12. [Star the Repository](#-star-the-repository)

---

## 🎯 Purpose & Use of This Project
Traditional recruitment pipelines suffer from extreme bottlenecks, relying on manual keyword-matching or slow, opaque reviews that fail to capture semantic context. 

**Purpose:** This project automates and intelligentizes candidate screening by leveraging **Dense Vector Embeddings (Sentence-Transformers)** and **Structured LLM Extraction (OpenAI)**. It matches resumes against job descriptions based on genuine contextual understanding rather than rigid keyword overlap, while enforcing strict **Role-Based Access Control (RBAC)** to protect candidate PII.

---

## ✨ Features
* **Semantic Vector Matching:** Replaces brittle TF-IDF matching with `all-MiniLM-L6-v2` embeddings for deep contextual candidate scoring.
* **Structured LLM Extraction:** Uses Pydantic schemas with OpenAI to reliably parse raw resumes into clean JSON objects (experience, skills, education, past companies).
* **Secure Document Parsing:** Validates real MIME types and securely handles multi-page PDF and DOCX uploads.
* **Recruiter Feedback Loop:** Dynamic scoring adjustments based on recruiter actions (Shortlisted/Rejected) that fine-tune ranking algorithms over time.
* **Multi-Format Reporting:** Instantaneous export of shortlisted candidates into professional CSV spreadsheets or PDF reports.
* **RBAC Security:** JSON Web Token (JWT) authorization protecting endpoints containing candidate PII.

---

## 📂 File Structure

```text
resume-screener-prod/
├── app/
│   ├── __init__.py          # Flask app factory & JWT initialization
│   ├── config.py            # Environment configuration management
│   ├── api/
│   │   ├── auth.py          # JWT decorators & RBAC role enforcement
│   │   └── feedback.py      # Recruiter action tracking & CSV/PDF exporting
│   └── services/
│       ├── database.py      # SQLite connection, schema setup & vector math
│       ├── nlp_engine.py    # Sentence-Transformers & OpenAI extraction
│       └── parser.py        # Secure PDF & DOCX MIME parsing
├── .env                     # Local environment variables (git-ignored)
├── Dockerfile               # Production container configuration
├── requirements.txt         # Project Python dependencies
└── README.md                # Project documentation

```

---

## 📊 System Architecture & Diagrams

### 1. Data Flow Diagram (DFD)

```text
 [Recruiter / User] 
        │
        ├── Uploads Resume (PDF/DOCX) ──> [Parser Service] ──> Extracts Raw Text
        │                                                           │
        │                                                           ▼
        │                                                [NLP Engine (LLM + Embeddings)]
        │                                                           │
        │       Inputs Job Description                              ▼
        └── (Query Vector) ──────────────> [Database Engine] ◄── Stores JSON Profile & Vector
                                                   │
                                                   ▼
                                         Computes Cosine Similarity
                                                   │
                                                   ▼
                                         Ranked Candidate Matches

```

### 2. Entity-Relationship (ER) Diagram

```text
┌────────────────────────┐              ┌──────────────────────────┐
│        RESUMES         │              │   RECRUITER_FEEDBACK     │
├────────────────────────┤              ├──────────────────────────┤
│ PK  id                 │◄─────────────┤ PK  id                   │
│     full_name          │   1      N   │ FK  candidate_id         │
│     email              │              │     job_id               │
│     total_exp_years    │              │     action               │
│     primary_skills     │              └──────────────────────────┘
│     embedding          │
│     feedback_boost     │
└────────────────────────┘

```

---

## ⚙️ Requirements & Prerequisites

* **Python:** `3.11+`
* **OS:** Windows CMD, PowerShell, Linux, or macOS
* **API Key:** An active OpenAI API key (`OPENAI_API_KEY`)

---

## 📥 Installation & Setup

Follow these steps to run the application locally on Windows CMD:

1. **Clone the Repository:**
```cmd
git clone [https://github.com/alok--kumar8765/resume-screener.git](https://github.com/alok--kumar8765/resume-screener.git)
cd resume-screener

```


2. **Create & Activate Virtual Environment:**
```cmd
python -m venv venv
venv\Scripts\activate.bat

```


3. **Install Dependencies:**
```cmd
pip install -r requirements.txt

```


4. **Configure Environment Variables:**
Create a `.env` file in the project root folder using Notepad:
```cmd
notepad .env

```


Add the following variables inside the `.env` file and save it:
```env
JWT_SECRET_KEY=your-super-secret-jwt-key
OPENAI_API_KEY=your_openai_api_key_here

```


5. **Run the Flask Development Server:**
```cmd
set FLASK_APP=app:create_app
flask run --host=0.0.0.0 --port=8000

```



---

## ⚖️ Pros & Cons

### Pros

* **High Semantic Accuracy:** Vector embeddings understand context (e.g., matching "Node.js developer" with "Backend JavaScript engineer").
* **Zero Infrastructure Overhead:** SQLite and local vector calculations mean you don't need heavy cloud databases to start developing.
* **Production-Minded Security:** Strict MIME validation prevents arbitrary file upload vulnerabilities.

### Cons

* **In-Memory Compute Scaling:** Using SQLite with in-memory NumPy cosine similarity works exceptionally well for development and moderate scale, but requires migration to a distributed vector store (like Qdrant or Milvus) for millions of enterprise resumes.
* **External API Dependency:** Relies on OpenAI for structured data extraction.

---

## 🚧 Limitations

* **Single-Node Execution:** The current development SQLite setup does not support concurrent write-heavy processing from multi-worker instances without locking overhead.
* **Language Support:** Heavily optimized for English resumes due to the chosen embedding space and LLM instructions.

---

## 🐛 Known Bugs & Vulnerabilities

* **Large File Uploads:** Uploading massive, multi-megabyte scanned PDFs without text layers may cause parser timeout bottlenecks before OCR is triggered.
* **Token Limits:** Excessively long resumes (e.g., academic CVs spanning 10+ pages) may exceed prompt token limits during OpenAI structured parsing.

---

## 🔮 Future Roadmap & Updates

* [ ] **Migration to Qdrant/Milvus:** Implement native distributed vector indexing to scale beyond tens of thousands of candidate profiles.
* [ ] **Asynchronous Task Queue:** Integrate Celery and Redis to handle bulk PDF ingestion asynchronously without blocking UI requests.
* [ ] **Local LLM Support:** Add Ollama integration (e.g., Llama 3) to allow fully offline, air-gapped deployments for enterprise privacy compliance.
* [ ] **Interactive Web Dashboard:** Build a complete frontend single-page dashboard using React/Tailwind.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the codebase, fix a bug, or add a feature:

1. Fork the Project (`https://github.com/alok--kumar8765/resume-screener/fork`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git origin push feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Star the Repository

If you found this project helpful or interesting, please give it a star on GitHub!

👉 **GitHub:** [alok--kumar8765](https://www.google.com/search?q=https://github.com/alok--kumar8765)
