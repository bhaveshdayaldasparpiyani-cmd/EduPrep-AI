import os
import sqlite3
import json
import random
import time
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "student_storage")

class StudentManager:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                mobile_no TEXT PRIMARY KEY,
                enrollment_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                branch TEXT NOT NULL,
                semester TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_store (
                mobile_no TEXT PRIMARY KEY,
                otp_code TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile_no TEXT,
                role TEXT,
                content TEXT,
                citations_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mobile_no) REFERENCES students (mobile_no)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile_no TEXT,
                score INTEGER,
                total_questions INTEGER,
                percentage REAL,
                topic TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mobile_no) REFERENCES students (mobile_no)
            )
        """)

        # New: Announcements Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT DEFAULT 'Normal',
                target_branch TEXT DEFAULT 'ALL',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # New: Activity Audit Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed default students if empty
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO students (mobile_no, enrollment_no, name, branch, semester) VALUES (?, ?, ?, ?, ?)",
                ("9876543210", "210200107001", "Rahul Patel", "Computer Engineering", "Sem 7")
            )
            cursor.execute(
                "INSERT INTO students (mobile_no, enrollment_no, name, branch, semester) VALUES (?, ?, ?, ?, ?)",
                ("9876543211", "210200107002", "Priya Sharma", "Information Technology", "Sem 7")
            )
            cursor.execute(
                "INSERT INTO students (mobile_no, enrollment_no, name, branch, semester) VALUES (?, ?, ?, ?, ?)",
                ("9876543212", "210200107003", "Ankit Varma", "AI & Data Science", "Sem 7")
            )

        # Seed sample announcement if empty
        cursor.execute("SELECT COUNT(*) FROM announcements")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO announcements (title, message, priority, target_branch) VALUES (?, ?, ?, ?)",
                ("GTU Mid-Semester Assessment Schedule", "All Semester 7 Engineering students must complete the AI Mock Viva and Syllabus Coverage audit before external jury submission.", "High", "ALL")
            )

        conn.commit()
        conn.close()

    # --- AUDIT LOGS ---
    def log_event(self, event_type: str, details: str):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO audit_logs (event_type, details) VALUES (?, ?)", (event_type, details))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_type, details, timestamp FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "event_type": r[1], "details": r[2], "timestamp": r[3]} for r in rows]

    # --- ANNOUNCEMENTS / NOTICE BOARD ---
    def create_announcement(self, title: str, message: str, priority: str = "Normal", target_branch: str = "ALL") -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO announcements (title, message, priority, target_branch) VALUES (?, ?, ?, ?)",
                (title.strip(), message.strip(), priority, target_branch)
            )
            conn.commit()
            conn.close()
            self.log_event("NOTICE_PUBLISHED", f"Published notice '{title}' for {target_branch}")
            return True
        except Exception:
            return False

    def get_active_announcements(self, branch: str = "ALL") -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if branch == "ALL":
            cursor.execute("SELECT id, title, message, priority, target_branch, created_at FROM announcements ORDER BY id DESC")
        else:
            cursor.execute("SELECT id, title, message, priority, target_branch, created_at FROM announcements WHERE target_branch = 'ALL' OR target_branch = ? ORDER BY id DESC", (branch,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "title": r[1], "message": r[2], "priority": r[3], "target_branch": r[4], "date": r[5]} for r in rows]

    def delete_announcement(self, ann_id: int) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
            conn.commit()
            conn.close()
            self.log_event("NOTICE_DELETED", f"Deleted notice #{ann_id}")
            return True
        except Exception:
            return False

    # --- OTP MANAGEMENT ---
    def generate_otp(self, mobile_no: str) -> str:
        mobile_no = mobile_no.strip()
        otp = str(random.randint(1000, 9999))
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO otp_store (mobile_no, otp_code, created_at) VALUES (?, ?, ?)",
            (mobile_no, otp, time.time())
        )
        conn.commit()
        conn.close()
        self.log_event("OTP_REQUEST", f"Generated OTP for {mobile_no}")
        return otp

    def verify_otp(self, mobile_no: str, input_otp: str, max_age_seconds: int = 300) -> Tuple[bool, str]:
        mobile_no = mobile_no.strip()
        input_otp = input_otp.strip()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code, created_at FROM otp_store WHERE mobile_no = ?", (mobile_no,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, "No OTP requested for this mobile number."
        stored_otp, created_at = row[0], row[1]
        if time.time() - created_at > max_age_seconds:
            return False, "OTP has expired. Please request a new one."
        if stored_otp != input_otp:
            return False, "Incorrect OTP. Please try again."

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM otp_store WHERE mobile_no = ?", (mobile_no,))
        conn.commit()
        conn.close()
        self.log_event("LOGIN_SUCCESS", f"Student {mobile_no} logged in successfully")
        return True, "OTP verified successfully!"

    # --- STUDENT LOOKUP & CRUD ---
    def is_mobile_registered(self, mobile_no: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM students WHERE mobile_no = ?", (mobile_no.strip(),))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def get_student_by_mobile(self, mobile_no: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mobile_no, enrollment_no, name, branch, semester, created_at FROM students WHERE mobile_no = ?", (mobile_no.strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "mobile_no": row[0],
                "enrollment_no": row[1],
                "name": row[2],
                "branch": row[3],
                "semester": row[4],
                "created_at": row[5]
            }
        return None

    def get_all_students(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mobile_no, enrollment_no, name, branch, semester, created_at FROM students ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "mobile_no": r[0],
                "enrollment_no": r[1],
                "name": r[2],
                "branch": r[3],
                "semester": r[4],
                "created_at": r[5]
            }
            for r in rows
        ]

    def register_student(self, mobile_no: str, enrollment_no: str, name: str, branch: str, semester: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        mobile_no = mobile_no.strip()
        enrollment_no = enrollment_no.strip().upper()
        name = name.strip()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (mobile_no, enrollment_no, name, branch, semester) VALUES (?, ?, ?, ?, ?)",
                (mobile_no, enrollment_no, name, branch, semester)
            )
            conn.commit()
            student_obj = {
                "mobile_no": mobile_no,
                "enrollment_no": enrollment_no,
                "name": name,
                "branch": branch,
                "semester": semester
            }
            os.makedirs(self.get_student_folder(mobile_no), exist_ok=True)
            conn.close()
            self.log_event("STUDENT_REGISTER", f"Enrolled student {name} ({enrollment_no})")
            return True, "Student registered successfully!", student_obj
        except sqlite3.IntegrityError as e:
            conn.close()
            if "UNIQUE constraint failed: students.mobile_no" in str(e):
                return False, "This mobile number is already registered.", None
            if "UNIQUE constraint failed: students.enrollment_no" in str(e):
                return False, "This GTU enrollment number is already registered.", None
            return False, f"Registration failed: {str(e)}", None

    def admin_update_student(self, original_mobile: str, new_mobile: str, new_enrollment: str, new_name: str, new_branch: str, new_semester: str) -> Tuple[bool, str]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE students 
                SET mobile_no = ?, enrollment_no = ?, name = ?, branch = ?, semester = ?
                WHERE mobile_no = ?
            """, (new_mobile.strip(), new_enrollment.strip().upper(), new_name.strip(), new_branch.strip(), new_semester.strip(), original_mobile.strip()))
            
            if original_mobile.strip() != new_mobile.strip():
                cursor.execute("UPDATE chat_history SET mobile_no = ? WHERE mobile_no = ?", (new_mobile.strip(), original_mobile.strip()))
                cursor.execute("UPDATE quiz_results SET mobile_no = ? WHERE mobile_no = ?", (new_mobile.strip(), original_mobile.strip()))
                
                old_dir = self.get_student_folder(original_mobile)
                new_dir = self.get_student_folder(new_mobile)
                if os.path.exists(old_dir) and old_dir != new_dir:
                    shutil.move(old_dir, new_dir)

            conn.commit()
            conn.close()
            self.log_event("STUDENT_UPDATE", f"Admin updated student {new_name} ({new_enrollment})")
            return True, "Student details updated successfully!"
        except Exception as e:
            conn.close()
            return False, f"Update failed: {str(e)}"

    def admin_delete_student(self, mobile_no: str) -> Tuple[bool, str]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM chat_history WHERE mobile_no = ?", (mobile_no,))
            cursor.execute("DELETE FROM quiz_results WHERE mobile_no = ?", (mobile_no,))
            cursor.execute("DELETE FROM otp_store WHERE mobile_no = ?", (mobile_no,))
            cursor.execute("DELETE FROM students WHERE mobile_no = ?", (mobile_no,))
            conn.commit()
            conn.close()

            folder = self.get_student_folder(mobile_no)
            if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)

            self.log_event("STUDENT_DELETE", f"Admin deleted student {mobile_no}")
            return True, "Student and all associated records deleted successfully!"
        except Exception as e:
            conn.close()
            return False, f"Delete failed: {str(e)}"

    def get_student_folder(self, mobile_no: str) -> str:
        folder = os.path.join(STORAGE_DIR, mobile_no)
        os.makedirs(folder, exist_ok=True)
        return folder

    # --- CHAT PERSISTENCE ---
    def save_chat_message(self, mobile_no: str, role: str, content: str, citations: list = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        citations_json = json.dumps(citations) if citations else "[]"
        cursor.execute(
            "INSERT INTO chat_history (mobile_no, role, content, citations_json) VALUES (?, ?, ?, ?)",
            (mobile_no, role, content, citations_json)
        )
        conn.commit()
        conn.close()

    def get_chat_history(self, mobile_no: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, citations_json FROM chat_history WHERE mobile_no = ? ORDER BY id ASC",
            (mobile_no,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for r in rows:
            citations = []
            if r[2]:
                try:
                    citations = json.loads(r[2])
                except Exception:
                    citations = []
            messages.append({"role": r[0], "content": r[1], "citations": citations})
        return messages

    def clear_chat_history(self, mobile_no: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE mobile_no = ?", (mobile_no,))
        conn.commit()
        conn.close()
        self.log_event("CHAT_CLEARED", f"Cleared chat history for {mobile_no}")

    # --- QUIZ PERSISTENCE & ANALYTICS ---
    def save_quiz_result(self, mobile_no: str, score: int, total: int, topic: str = "General GTU Quiz"):
        pct = (score / total) * 100 if total > 0 else 0.0
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO quiz_results (mobile_no, score, total_questions, percentage, topic) VALUES (?, ?, ?, ?, ?)",
            (mobile_no, score, total, pct, topic)
        )
        conn.commit()
        conn.close()
        self.log_event("QUIZ_COMPLETED", f"Student {mobile_no} scored {score}/{total} ({pct:.1f}%) in {topic}")

    def get_student_quiz_analytics(self, mobile_no: str) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT score, total_questions, percentage, topic, timestamp FROM quiz_results WHERE mobile_no = ? ORDER BY id DESC",
            (mobile_no,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"total_attempts": 0, "average_score": 0.0, "highest_score": 0.0, "history": []}
        
        percentages = [r[2] for r in rows]
        return {
            "total_attempts": len(rows),
            "average_score": sum(percentages) / len(percentages),
            "highest_score": max(percentages),
            "history": [{"score": f"{r[0]}/{r[1]}", "percentage": r[2], "topic": r[3], "date": r[4]} for r in rows]
        }

    def get_all_quiz_records_admin(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.id, s.name, s.enrollment_no, q.mobile_no, s.branch, q.score, q.total_questions, q.percentage, q.topic, q.timestamp
            FROM quiz_results q
            JOIN students s ON q.mobile_no = s.mobile_no
            ORDER BY q.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "student_name": r[1],
                "enrollment_no": r[2],
                "mobile_no": r[3],
                "branch": r[4],
                "score": f"{r[5]}/{r[6]}",
                "percentage": r[7],
                "topic": r[8],
                "date": r[9]
            }
            for r in rows
        ]

    def delete_quiz_record_admin(self, quiz_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_results WHERE id = ?", (quiz_id,))
        conn.commit()
        conn.close()
        self.log_event("QUIZ_RECORD_DELETED", f"Deleted quiz record #{quiz_id}")

    # --- ADVANCED BATCH ANALYTICS & RANKINGS ---
    def get_class_rankings(self) -> List[Dict[str, Any]]:
        """Compute institutional rank list based on cumulative average scores."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.name, s.enrollment_no, s.branch, s.semester,
                   COUNT(q.id) as attempts,
                   AVG(q.percentage) as avg_score,
                   MAX(q.percentage) as max_score
            FROM students s
            LEFT JOIN quiz_results q ON s.mobile_no = q.mobile_no
            GROUP BY s.mobile_no
            ORDER BY avg_score DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        ranked_list = []
        for rank, r in enumerate(rows, start=1):
            avg = r[5] if r[5] is not None else 0.0
            max_s = r[6] if r[6] is not None else 0.0
            attempts = r[4]
            status = "🌟 Distinction" if avg >= 75 else ("👍 First Class" if avg >= 60 else ("⚠️ Needs Attention" if attempts > 0 else "⏳ Not Attempted"))
            ranked_list.append({
                "Rank": f"#{rank}",
                "Name": r[0],
                "Enrollment": r[1],
                "Branch": r[2],
                "Semester": r[3],
                "Quizzes": attempts,
                "Average Score (%)": f"{avg:.1f}%",
                "Highest Score (%)": f"{max_s:.1f}%",
                "Status": status
            })
        return ranked_list

    def get_branch_analytics(self) -> Dict[str, Any]:
        """Branch-wise breakdown of average performance."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.branch, COUNT(DISTINCT s.mobile_no) as total_students,
                   COUNT(q.id) as total_quizzes,
                   AVG(q.percentage) as branch_avg
            FROM students s
            LEFT JOIN quiz_results q ON s.mobile_no = q.mobile_no
            GROUP BY s.branch
        """)
        rows = cursor.fetchall()
        conn.close()

        analytics = {}
        for r in rows:
            analytics[r[0]] = {
                "students": r[1],
                "quizzes": r[2],
                "avg_score": round(r[3] if r[3] is not None else 0.0, 1)
            }
        return analytics

    def get_system_overview_stats(self) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM quiz_results")
        total_quizzes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM announcements")
        total_notices = cursor.fetchone()[0]
        conn.close()
        return {
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "total_chats": total_chats,
            "total_notices": total_notices
        }
