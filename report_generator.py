import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_student_certificate_pdf(student_info: dict, analytics: dict) -> bytes:
    """Generate a clean, high-resolution GTU Study Certificate & Performance Report PDF."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Outer decorative border
    c.setStrokeColor(colors.HexColor("#0D47A1"))
    c.setLineWidth(3)
    c.rect(25, 25, width - 50, height - 50)
    
    c.setStrokeColor(colors.HexColor("#1E88E5"))
    c.setLineWidth(1)
    c.rect(30, 30, width - 60, height - 60)

    # University Header
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 65, "GUJARAT TECHNOLOGICAL UNIVERSITY")
    
    c.setFillColor(colors.HexColor("#546E7A"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 82, "AI-Powered Academic Excellence & Internship Assessment Portal")

    c.setStrokeColor(colors.HexColor("#B0BEC5"))
    c.setLineWidth(1)
    c.line(50, height - 95, width - 50, height - 95)

    # Certificate Title
    c.setFillColor(colors.HexColor("#1565C0"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 130, "ACADEMIC PERFORMANCE & MASTERY REPORT")

    c.setFillColor(colors.HexColor("#37474F"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 150, "This is to certify the academic evaluation and self-assessment completed by:")

    # Student Name Box
    c.setFillColor(colors.HexColor("#E3F2FD"))
    c.rect(80, height - 205, width - 160, 40, fill=1, stroke=0)
    
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 190, student_info.get("name", "Student Name").upper())

    # Details Grid
    c.setFillColor(colors.HexColor("#263238"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(80, height - 230, f"GTU Enrollment No :  {student_info.get('enrollment_no', 'N/A')}")
    c.drawString(330, height - 230, f"Registered Mobile :  +91 {student_info.get('mobile_no', 'N/A')}")
    c.drawString(80, height - 248, f"Branch / Discipline:  {student_info.get('branch', 'Engineering')}")
    c.drawString(330, height - 248, f"Current Semester   :  {student_info.get('semester', 'Sem 7')}")

    # Performance Stats Box
    c.setStrokeColor(colors.HexColor("#90CAF9"))
    c.setFillColor(colors.HexColor("#FAFAFA"))
    c.rect(80, height - 345, width - 160, 80, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, height - 280, "ASSESSMENT METRICS & LEARNING OUTCOMES")

    c.setFillColor(colors.HexColor("#37474F"))
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 302, f"• Total Interactive Quizzes Completed:  {analytics.get('total_attempts', 0)}")
    c.drawString(100, height - 318, f"• Cumulative Average Score Percentage:  {analytics.get('average_score', 0.0):.1f}%")
    c.drawString(100, height - 334, f"• Highest Assessment Score Achieved  :  {analytics.get('highest_score', 0.0):.1f}%")

    # Competencies verified
    c.setFillColor(colors.HexColor("#0D47A1"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(80, height - 375, "VERIFIED TECHNICAL COMPETENCIES & MODULES:")
    
    competencies = [
        "1. AI Intelligent Agents & Search Algorithms (BFS, DFS, A* Heuristic Search)",
        "2. Machine Learning Foundations (Supervised, Unsupervised & Bias-Variance Tradeoff)",
        "3. Decision Trees, Entropy, Information Gain & Overfitting Regularization",
        "4. Retrieval-Augmented Generation (RAG) Architecture & Vector Embeddings Mastery"
    ]
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#455A64"))
    y_pos = height - 395
    for comp in competencies:
        c.drawString(80, y_pos, comp)
        y_pos -= 16

    # Date and Signatures
    current_date = datetime.now().strftime("%B %d, %Y")
    c.setFillColor(colors.HexColor("#263238"))
    c.setFont("Helvetica", 10)
    c.drawString(80, 80, f"Date of Issue: {current_date}")
    
    # Signature Box
    c.setStrokeColor(colors.HexColor("#B0BEC5"))
    c.line(width - 240, 85, width - 80, 85)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width - 160, 70, "EduPrep AI Evaluation Engine")
    c.setFont("Helvetica", 8)
    c.drawCentredString(width - 160, 58, "GTU AI Internship Assessment")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
