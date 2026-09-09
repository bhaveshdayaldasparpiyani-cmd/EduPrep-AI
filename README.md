# 🎓 EduPrep AI: RAG-based GTU Exam Prep & Academic Assistant

> **Gujarat Technological University (GTU) 15-Days AI Internship Project**  
> Developed using Python, Generative AI (Google Gemini LLM), RAG Architecture, FAISS Vector Database, and Streamlit.

---

## 📌 Project Overview
**EduPrep AI** is an intelligent academic platform designed for university students to interact with their syllabus, lecture notes, and textbooks. Using **Retrieval-Augmented Generation (RAG)**, it enables accurate question-answering with page citations, generates authentic **GTU 3/4/7 Marks Exam Papers**, produces **Interactive Self-Assessment Quizzes**, and provides **Last-Minute Revision Cheat-Sheets**.

---

## 🚀 Key Features

1. **💬 Real-Time Academic Chatbot (RAG)**:
   - Queries answered strictly from uploaded PDF course notes.
   - Zero hallucination with collapsible **source citations** (File Name, Page Number, and Context Snippet).

2. **📝 GTU Exam Paper Generator**:
   - Generates questions according to standard GTU Exam Blueprint:
     - **3 Marks**: Definitions, short concepts, basic differences.
     - **4 Marks**: Block diagram explanations, comparisons, short algorithms.
     - **7 Marks**: Detailed analytical/descriptive questions with step-by-step model answers.
   - One-click Markdown export.

3. **🧠 Interactive MCQ Quiz Generator**:
   - Automated self-testing with randomized questions from your study material.
   - Instant score calculation, progress bar, and comprehensive answer explanations.

4. **📌 Last-Minute Revision & Formulas**:
   - Generates high-yield cheat sheets with core definitions, formulas, and high-frequency exam topics.

---

## 🏗️ System Architecture

```
[Student Uploads PDF Notes]
            │
            ▼
   [pypdf Text Extraction]
            │
            ▼
[Semantic Chunking (800 chars, 150 overlap)]
            │
            ▼
  [Vector Embeddings (Gemini Embeddings)]
            │
            ▼
      [FAISS Vector Store]
            ▲
            │ (Vector Similarity Search)
            ▼
[Student Query] ──► [Context Assembly + GTU Prompt] ──► [Gemini 1.5 Flash LLM] ──► [Streamlit UI]
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.10+ installed
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

### 2. Clone / Open Project Directory
```bash
cd C:\Users\admin\.gemini\antigravity\scratch\gtu_ai_academic_bot
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file from `.env.example` or paste your key directly in the web UI sidebar:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 5. Generate Built-in Sample Notes (Optional)
```bash
python generate_sample_pdf.py
```

### 6. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Project Directory Structure
```
gtu_ai_academic_bot/
├── app.py                     # Main Streamlit web application
├── rag_engine.py              # PDF Parser, Vector Indexer & RAG retrieval pipeline
├── prompts.py                 # Custom GTU Academic Prompt Templates
├── generate_sample_pdf.py     # Generator for built-in sample GTU AI notes
├── sample_notes/              # Sample PDF notes for instant testing
│   └── AI_Machine_Learning_GTU_Notes.pdf
├── requirements.txt           # Python dependencies
├── .env.example               # Template for API Key
├── README.md                  # Project documentation
└── gtu_viva_guide.md          # 15-Day Internship report summary & Viva Q&A
```

---

## 👨‍💻 Tech Stack
- **Programming Language:** Python 3.11
- **LLM & Embeddings:** Google Gemini Flash (`gemini-1.5-flash`, `text-embedding-004`)
- **Vector Database:** FAISS (Facebook AI Similarity Search)
- **PDF Processing:** PyPDF
- **Frontend / UI:** Streamlit
