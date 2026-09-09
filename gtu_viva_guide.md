# 🎯 GTU 15-Days Internship Project: Complete Viva & Report Guide

> **Project Title:** EduPrep AI: Multi-Student RAG Academic Assistant & GTU Examination Prep Suite  
> **Domain:** Generative AI, Retrieval-Augmented Generation (RAG), Multimodal Vision, Speech Synthesis, SQLite3  

---

## 🌟 Complete 8-Feature Academic Architecture

| Tab / Module | Key Technical Capability | GTU Viva Weightage |
| :--- | :--- | :--- |
| **1. Multilingual Q&A & Voice Audio** | Answers in English, Gujarati (ગુજરાતી), or Hindi + Speech Synthesis playback. | High practical & regional appeal |
| **2. AI Mock Viva Examiner** | 30-Marks simulated GTU external viva with live questions & comprehensive marksheet evaluation. | Highly rated by professors |
| **3. Digital Flashcards** | Active recall cards with 3D Flip animation for last-minute formula revision. | Best active learning tool |
| **4. Handwritten Notes Scanner** | Multimodal Gemini Vision AI for OCR transcription of class notebooks & blackboard diagrams. | Modern Computer Vision + LLM |
| **5. GTU Syllabus Coverage Audit** | Analyzes % of syllabus covered in notes & detects missing high-yield exam topics. | Curriculum alignment |
| **6. Interactive MCQ Quiz** | Live self-assessment with score tracking & step-by-step explanations. | Knowledge verification |
| **7. GTU Exam Paper Generator** | Formats questions into official 3, 4, and 7 marks blueprints with model solutions. | University exam standard |
| **8. Performance Certificate PDF** | Generates official GTU Performance Certificate & Internship Study Report in PDF format. | Direct submission deliverable |

---

## 📅 15-Day Internship Weekly Activity Log (For Internship Report / Diary)

| Week / Days | Activity & Progress Summary |
| :--- | :--- |
| **Day 1 - 2** | Requirement Analysis, Literature Review of LLMs, Multi-User Auth Systems & RAG Architecture. |
| **Day 3 - 5** | Database Design (`students.db` via SQLite3) for Mobile Number Auth, OTP verification, and Quiz Analytics. |
| **Day 6 - 8** | Implemented `rag_engine.py` (PDF Parsing via PyPDF, Semantic Chunking, Vector Similarity & Gemini LLM). |
| **Day 9 - 11** | Developed GTU-specific prompt templates for 3/4/7 Marks Questions, MCQ Quiz & Revision Sheets (`prompts.py`). |
| **Day 12 - 13** | Built Multilingual Audio (gTTS), Vision OCR for handwritten notes, Mock Viva Examiner & Flashcards. |
| **Day 14 - 15** | Implemented 1-Click PDF Certificate Generator (`report_generator.py`), system testing, report writing & PPT preparation. |

---

## 🎓 Top GTU Viva Questions & Answers

### Q1. How does the Multimodal Vision OCR work in this project?
**Answer:**  
Using Google Gemini Vision API (`image/jpeg` payload), the system accepts photos of handwritten class notes or blackboard diagrams. The multimodal LLM transcribes handwritten text/equations into LaTeX, analyzes diagrams/flowcharts, and automatically inserts the extracted context as a semantic chunk into the student's vector knowledge base.

---

### Q2. How is the 30-Marks AI Mock Viva evaluated?
**Answer:**  
The AI is instructed with a specialized Role-Based Prompt to act as a GTU Senior External Examiner. It evaluates the student's answers on three official parameters:
1. Technical Depth & Conceptual Clarity (10 Marks)
2. Precision & Academic Terminology (10 Marks)
3. Real-World Engineering Application (10 Marks)
It outputs a formal marksheet with score breakdown and 3 focus topics for revision.

---

### Q3. How does the Voice Audio feature work?
**Answer:**  
When an answer is generated (in English, Gujarati, or Hindi), `gTTS` (Google Text-to-Speech) converts the synthesized text into an MP3 audio buffer in real-time, allowing students to listen to the explanation hands-free.


---

## 🛡️ University Administrator & Database Control Center

### Access Credentials:
- **Admin Password / PIN:** `admin123` (or `gtu2026`)
- **Access Point:** Click the **`🛡️ Admin Portal`** tab on the Login Page, or click **`🛡️ Admin Mode`** in the student sidebar.

### Admin Capabilities (CRUD):
1. **Student Directory & Details Editor:**
   - Modify any student's Name, GTU Enrollment Number, Mobile Number, Branch, or Semester.
   - Delete obsolete or graduated student profiles and their data.
   - Direct manual student enrollment without OTP.
2. **Institution Gradebook & Quiz Records:**
   - View complete quiz logs and assessment scores across all branches.
   - Correct or delete erroneous quiz records.
3. **Student Storage & Cache Inspector:**
   - Inspect uploaded notes and wipe student chat history/cache.
4. **Global System & AI Configuration:**
   - Update API Key system-wide in `.env`.
   - 1-Click JSON/CSV database backup.


---

## 🛡️ GTU University Administrator Operations Suite (6 Power Tabs)

| Admin Tab | Enterprise Capabilities |
| :--- | :--- |
| **1. 👥 Student Directory & Details Editor** | Full CRUD: Edit Name, Enrollment, Mobile, Branch, Semester, delete obsolete profiles, or add new students directly. |
| **2. 📈 Batch Analytics & Branch Performance** | Branch-wise score averages (CE vs IT vs AI), distinction ratios, and automated identification of at-risk students who need remediation. |
| **3. 📢 University Broadcast & Live Notice Board** | Publish official GTU exam dates and guidelines which dynamically appear on student dashboards. |
| **4. 🏆 Class Rank List & Gradebook** | Auto-ranked batch leaderboard (#1, #2, #3), complete quiz marksheet, and individual score correction. |
| **5. 📜 Real-Time Security & Activity Audit Log** | Immutable log tracking OTP generation, student logins, exam completions, and database changes with exact timestamps. |
| **6. ⚙️ AI Diagnostics & Database Backup** | Global Gemini API key configuration and 1-click JSON backup of all university records. |


---

## 📱 Android Mobile Application Architecture (`android_app/`)

### Key Components:
1. **Android Studio Native Wrapper (`com.gtu.eduprep`):**
   - Built with Android SDK 34, AndroidX, and Material Components.
   - `MainActivity.java` with hardware-accelerated WebView, custom user-agent, DOM storage, and pull-to-refresh.
   - Android `WebChromeClient` with file chooser integration to capture live camera photos for Gemini Vision OCR and upload PDF syllabus notes.
2. **1-Tap Android WebAPK / PWA Support:**
   - Standalone display mode with `manifest.json` for installing directly onto Android phone home screens.
