import os
import io
import shutil
import json
import importlib
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_FILE_PATH, override=True)

try:
    if "GEMINI_API_KEY" in st.secrets and not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

import prompts
import rag_engine
import student_manager
import report_generator
importlib.reload(prompts)
importlib.reload(rag_engine)
importlib.reload(student_manager)
importlib.reload(report_generator)

from rag_engine import RAGEngine
from student_manager import StudentManager
from report_generator import generate_student_certificate_pdf

sm = StudentManager()

st.set_page_config(
    page_title="EduPrep AI - GTU Academic & Admin Suite",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(124, 58, 237, 0.08) 100%);
        border: 1px solid rgba(124, 58, 237, 0.15);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .admin-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #311042 100%);
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-radius: 16px;
        padding: 1.6rem 2rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: linear-gradient(90deg, #E0E7FF 0%, #EDE9FE 100%);
        color: #4F46E5;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .gradient-text {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #DB2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 0.3rem;
    }
    .student-id-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1.3rem;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.4);
        position: relative;
        margin-bottom: 1.2rem;
    }
    .id-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .id-chip {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    .status-dot {
        font-size: 0.7rem;
        font-weight: 700;
        color: #4ADE80;
    }
    .id-name {
        font-size: 1.2rem;
        font-weight: 800;
    }
    .id-meta {
        font-size: 0.82rem;
        color: #C7D2FE;
        margin-top: 0.2rem;
    }
    .flashcard-wrapper {
        background: #FFFFFF;
        border: 2px solid #6366F1;
        border-radius: 20px;
        padding: 2.2rem;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.15);
        margin-bottom: 1.5rem;
    }
    .flashcard-front {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1E293B;
    }
    .flashcard-back {
        font-size: 1.15rem;
        font-weight: 500;
        color: #065F46;
        background: #ECFDF5;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #10B981;
        line-height: 1.6;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E293B;
    }
    .metric-lbl {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    .notice-card {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 5px solid #F59E0B;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.1);
    }
    .sms-container {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #22C55E;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #166534;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def save_api_key_to_env(key_str: str):
    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"GEMINI_API_KEY={key_str.strip()}\n")
    os.environ["GEMINI_API_KEY"] = key_str.strip()

for key, default in [
    ("is_admin", False),
    ("logged_in_student", None), ("login_otp_sent", False), ("login_otp_code", None),
    ("login_mobile", ""), ("reg_otp_sent", False), ("reg_otp_code", None),
    ("reg_data", {}), ("rag_engine", None), ("indexed", False),
    ("stats", {"chunks": 0, "pages": 0, "files": 0}), ("quiz_data", None),
    ("quiz_submitted", False), ("user_answers", {}), ("flashcards_data", None),
    ("card_index", 0), ("card_flipped", False), ("viva_questions", []),
    ("viva_answers", {}), ("viva_result", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ==============================================================================
# VIEW 1: SUPERCHARGED ADMIN CONTROL CENTER (When Admin is Logged In)
# ==============================================================================
if st.session_state.is_admin:
    st.markdown("""
    <div class="admin-banner">
        <div style="font-size: 0.8rem; font-weight: 700; color: #F43F5E; letter-spacing: 1px; margin-bottom: 0.4rem;">🛡️ GTU UNIVERSITY CONTROLLER • SYSTEM ADMIN PANEL</div>
        <div style="font-size: 2.2rem; font-weight: 800; margin: 0;">Academic Administration & Operations Suite</div>
        <div style="font-size: 0.95rem; color: #FDA4AF; margin-top: 0.3rem;">Manage students, inspect batch analytics, broadcast university notices, and audit security logs.</div>
    </div>
    """, unsafe_allow_html=True)

    sys_stats = sm.get_system_overview_stats()
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: #4F46E5;">{sys_stats['total_students']}</div>
            <div class="metric-lbl">Total Students</div>
        </div>
        """, unsafe_allow_html=True)
    with col_a2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: #059669;">{sys_stats['total_quizzes']}</div>
            <div class="metric-lbl">Quizzes Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with col_a3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: #D97706;">{sys_stats['total_chats']}</div>
            <div class="metric-lbl">AI Conversations</div>
        </div>
        """, unsafe_allow_html=True)
    with col_a4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: #E11D48;">{sys_stats['total_notices']}</div>
            <div class="metric-lbl">Active Notices</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("🚪 Exit Admin Portal & Return to Student Mode", type="secondary"):
        st.session_state.is_admin = False
        st.rerun()

    st.divider()

    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6 = st.tabs([
        "👥 Student Directory & Details Editor",
        "📈 Batch Analytics & Performance",
        "📢 University Notice Board & Broadcast",
        "🏆 Class Rank List & Gradebook",
        "📜 System Security & Audit Log",
        "⚙️ AI Diagnostics & DB Backup"
    ])

    # --- ADMIN TAB 1: STUDENT DIRECTORY & CRUD EDITOR ---
    with admin_tab1:
        st.subheader("👥 Student Directory (Edit / Update / Delete Records)")
        st.caption("View and modify any student's name, GTU enrollment number, mobile, branch, or semester.")

        all_students_list = sm.get_all_students()

        if all_students_list:
            st.dataframe(all_students_list, use_container_width=True)
        else:
            st.info("No students registered yet.")

        st.divider()
        col_ed1, col_ed2 = st.columns([1, 1])

        with col_ed1:
            st.markdown("#### ✏️ Edit Existing Student Details")
            if all_students_list:
                selected_edit_str = st.selectbox(
                    "Select Student to Edit:",
                    options=[f"{s['name']} - GTU: {s['enrollment_no']} (Mob: {s['mobile_no']})" for s in all_students_list],
                    key="sel_edit_student"
                )
                
                selected_mob = selected_edit_str.split("Mob: ")[-1].replace(")", "").strip()
                s_obj = sm.get_student_by_mobile(selected_mob)

                if s_obj:
                    with st.form("admin_edit_student_form"):
                        e_name = st.text_input("Full Name", value=s_obj["name"])
                        e_enroll = st.text_input("GTU Enrollment No.", value=s_obj["enrollment_no"])
                        e_mob = st.text_input("Mobile Number", value=s_obj["mobile_no"])
                        
                        e_col_b, e_col_s = st.columns(2)
                        with e_col_b:
                            branches = ["Computer Engineering", "Information Technology", "AI & Data Science", "Electronics & Comm.", "Mechanical Engg", "Civil Engg"]
                            b_idx = branches.index(s_obj["branch"]) if s_obj["branch"] in branches else 0
                            e_branch = st.selectbox("Branch", branches, index=b_idx)
                        with e_col_s:
                            sems = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"]
                            s_idx = sems.index(s_obj["semester"]) if s_obj["semester"] in sems else 6
                            e_sem = st.selectbox("Semester", sems, index=s_idx)

                        save_changes_btn = st.form_submit_button("💾 Save Updated Student Details", type="primary")

                        if save_changes_btn:
                            ok, msg = sm.admin_update_student(
                                original_mobile=s_obj["mobile_no"],
                                new_mobile=e_mob,
                                new_enrollment=e_enroll,
                                new_name=e_name,
                                new_branch=e_branch,
                                new_semester=e_sem
                            )
                            if ok:
                                st.success("✅ Student details updated successfully in database!")
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                st.info("No students available to edit.")

        with col_ed2:
            st.markdown("#### 🗑️ Delete Student Account")
            if all_students_list:
                del_student_str = st.selectbox(
                    "Select Student to Remove:",
                    options=[f"{s['name']} - GTU: {s['enrollment_no']} ({s['mobile_no']})" for s in all_students_list],
                    key="sel_del_student"
                )
                del_mob = del_student_str.split("(")[-1].replace(")", "").strip()
                
                st.warning("⚠️ Deleting a student removes their profile, quiz records, and uploaded notes permanently.")
                if st.button(f"🗑️ Delete Student ({del_mob})", type="secondary"):
                    ok, msg = sm.admin_delete_student(del_mob)
                    if ok:
                        st.success("✅ Student deleted successfully!")
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("#### ➕ Add Student Manually (Direct Admin Enrollment)")
            with st.form("admin_add_student_form"):
                add_name = st.text_input("Student Name", placeholder="e.g. Ankit Sharma")
                add_enroll = st.text_input("Enrollment No.", placeholder="e.g. 210200107009")
                add_mob = st.text_input("Mobile No.", placeholder="e.g. 9876543299")
                add_b = st.selectbox("Branch", ["Computer Engineering", "Information Technology", "AI & Data Science", "Mechanical Engg", "Civil Engg"])
                add_s = st.selectbox("Semester", ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"], index=6)
                
                if st.form_submit_button("➕ Enroll Student"):
                    if add_name and add_enroll and add_mob:
                        ok, msg, _ = sm.register_student(add_mob, add_enroll, add_name, add_b, add_s)
                        if ok:
                            st.success("✅ Student enrolled successfully!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill all fields.")

    # --- ADMIN TAB 2: BATCH ANALYTICS & PERFORMANCE ---
    with admin_tab2:
        st.subheader("📈 Institutional & Branch-Wise Academic Analytics")
        st.caption("Deep performance insights across engineering branches and batches.")
        
        branch_stats = sm.get_branch_analytics()
        
        cols = st.columns(len(branch_stats) if branch_stats else 1)
        for idx, (b_name, b_data) in enumerate(branch_stats.items()):
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #3B82F6;">
                    <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.5rem;">{b_name}</div>
                    <div class="metric-val" style="color: #2563EB;">{b_data['avg_score']}%</div>
                    <div class="metric-lbl">Branch Average Mastery</div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.5rem;">👥 {b_data['students']} Students • 📝 {b_data['quizzes']} Quizzes</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🎯 Academic Action Plan & Student Intervention")
        rankings = sm.get_class_rankings()
        
        at_risk = [r for r in rankings if "Needs Attention" in r["Status"]]
        distinction = [r for r in rankings if "Distinction" in r["Status"]]
        
        c_at1, c_at2 = st.columns(2)
        with c_at1:
            st.markdown(f"**🌟 Distinction Performers (≥75%):** `{len(distinction)} Students`")
            for d in distinction:
                st.success(f"👨‍🎓 {d['Name']} ({d['Enrollment']}) - {d['Average Score (%)']} in {d['Branch']}")
        with c_at2:
            st.markdown(f"**⚠️ Focus Intervention Students (<60%):** `{len(at_risk)} Students`")
            if at_risk:
                for a in at_risk:
                    st.warning(f"👨‍🎓 {a['Name']} ({a['Enrollment']}) - {a['Average Score (%)']} in {a['Branch']} - Recommended for Revision")
            else:
                st.info("No at-risk students found! All active scholars are performing well.")

    # --- ADMIN TAB 3: UNIVERSITY BROADCAST & NOTICE BOARD ---
    with admin_tab3:
        st.subheader("📢 University Notice Board & Live Broadcast Ticker")
        st.caption("Publish official academic alerts that instantly display on all student dashboards.")
        
        col_pub, col_notices = st.columns([1, 1])
        
        with col_pub:
            st.markdown("#### 📝 Create New University Announcement")
            with st.form("admin_notice_form"):
                n_title = st.text_input("Notice Title", placeholder="e.g. GTU External Viva Date Announced")
                n_msg = st.text_area("Notice Body / Message", placeholder="e.g. The External Viva for AI & ML will be conducted on March 5th. Prepare your 15-day logbook.")
                n_priority = st.selectbox("Priority Level", ["Normal", "High", "Urgent Alert 🔥"])
                n_branch = st.selectbox("Target Branch", ["ALL", "Computer Engineering", "Information Technology", "AI & Data Science"])
                
                if st.form_submit_button("📢 Publish Announcement (Press Enter)", type="primary"):
                    if n_title and n_msg:
                        ok = sm.create_announcement(n_title, n_msg, n_priority, n_branch)
                        if ok:
                            st.success("✅ Announcement published to student portal!")
                            st.rerun()
                        else:
                            st.error("Failed to publish announcement.")
                    else:
                        st.warning("Please fill in title and message.")

        with col_notices:
            st.markdown("#### 📌 Active Notices & Broadcasts")
            active_notices = sm.get_active_announcements()
            if active_notices:
                for ann in active_notices:
                    with st.expander(f"📢 [{ann['priority']}] {ann['title']} (Target: {ann['target_branch']})", expanded=True):
                        st.write(ann["message"])
                        st.caption(f"🗓️ Date: {ann['date']}")
                        if st.button("🗑️ Delete Notice", key=f"del_ann_{ann['id']}"):
                            sm.delete_announcement(ann["id"])
                            st.success("Notice deleted.")
                            st.rerun()
            else:
                st.info("No active announcements.")

    # --- ADMIN TAB 4: CLASS RANK LIST & GRADEBOOK ---
    with admin_tab4:
        st.subheader("🏆 Official Class Rank List & Institution Marksheet")
        st.caption("Auto-computed institutional ranks based on AI assessment mastery.")
        
        ranks = sm.get_class_rankings()
        if ranks:
            st.dataframe(ranks, use_container_width=True)
        else:
            st.info("No rankings available yet.")

        st.divider()
        st.subheader("📊 Individual Quiz Logs & Grade Correction")
        all_quizzes = sm.get_all_quiz_records_admin()
        if all_quizzes:
            st.dataframe(all_quizzes, use_container_width=True)
            del_qid = st.number_input("Enter Quiz Record ID to Remove/Correct:", min_value=1, step=1)
            if st.button("🗑️ Remove Quiz Record"):
                sm.delete_quiz_record_admin(del_qid)
                st.success(f"Quiz Record #{del_qid} removed.")
                st.rerun()
        else:
            st.info("No quiz records logged.")

    # --- ADMIN TAB 5: SECURITY AUDIT LOGS ---
    with admin_tab5:
        st.subheader("📜 Real-Time Security & Activity Audit Log")
        st.caption("Live immutable trail of student logins, OTP events, exam submissions, and admin modifications.")
        
        audits = sm.get_audit_logs(limit=50)
        if audits:
            st.dataframe(audits, use_container_width=True)
        else:
            st.info("No events logged yet.")

    # --- ADMIN TAB 6: AI DIAGNOSTICS & BACKUP ---
    with admin_tab6:
        st.subheader("⚙️ Global AI Configuration & Full Database Backup")
        
        curr_key = os.getenv("GEMINI_API_KEY", "")
        with st.form("admin_global_key_form"):
            new_global_key = st.text_input("Global Gemini API Key", value=curr_key, type="password")
            if st.form_submit_button("💾 Save Global API Key"):
                save_api_key_to_env(new_global_key)
                st.success("Global API key updated successfully in .env!")
                st.rerun()

        st.divider()
        st.subheader("📦 Institutional Database Export")
        if st.button("📥 Export Complete Student & Gradebook Backup (JSON)"):
            all_s_json = json.dumps({
                "students": sm.get_all_students(),
                "rankings": sm.get_class_rankings(),
                "quizzes": sm.get_all_quiz_records_admin(),
                "announcements": sm.get_active_announcements()
            }, indent=2)
            st.download_button("Download gtu_complete_backup.json", data=all_s_json, file_name="gtu_complete_backup.json", mime="application/json")

# ==============================================================================
# VIEW 2: STUDENT LOGIN & REGISTRATION (When Not Logged In & Not Admin)
# ==============================================================================
elif st.session_state.logged_in_student is None:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem 1rem 1rem;">
        <img src="https://img.icons8.com/clouds/200/graduation-cap.png" width="120" style="filter: drop-shadow(0 10px 15px rgba(99, 102, 241, 0.3));">
        <div class="hero-title" style="font-size: 2.6rem;">EduPrep <span class="gradient-text">AI Suite</span></div>
        <div class="hero-subtitle" style="font-size: 1.1rem; margin-top: 0.5rem;">Gujarat Technological University (GTU) • Next-Gen Student & Admin Portal</div>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    
    with auth_col2:
        tab_login, tab_register, tab_admin_login = st.tabs(["📱 Mobile OTP Login", "📝 Register Student", "🛡️ Admin Portal"])
        
        # --- TAB 1: LOGIN WITH MOBILE OTP ---
        with tab_login:
            st.markdown("#### Student Authentication")
            
            with st.form("login_mobile_send_form"):
                mobile_input = st.text_input("📱 Mobile Number (10 Digits)", placeholder="e.g. 9876543210", key="mob_in")
                col_otp_btn, col_demo_btn = st.columns([2, 1])
                with col_otp_btn:
                    send_otp_btn = st.form_submit_button("📩 Send Login OTP", type="primary", use_container_width=True)
                with col_demo_btn:
                    demo_fill_btn = st.form_submit_button("⚡ Demo (Rahul)", use_container_width=True)

                if demo_fill_btn:
                    st.session_state.login_mobile = "9876543210"
                    otp = sm.generate_otp("9876543210")
                    st.session_state.login_otp_sent = True
                    st.session_state.login_otp_code = otp
                    st.rerun()

                if send_otp_btn:
                    if len(mobile_input.strip()) == 10 and mobile_input.strip().isdigit():
                        if sm.is_mobile_registered(mobile_input.strip()):
                            otp = sm.generate_otp(mobile_input.strip())
                            st.session_state.login_otp_sent = True
                            st.session_state.login_otp_code = otp
                            st.session_state.login_mobile = mobile_input.strip()
                            st.rerun()
                        else:
                            st.error("Mobile number is not registered. Please register first.")
                    else:
                        st.warning("Please enter a valid 10-digit mobile number.")

            if st.session_state.login_otp_sent and st.session_state.login_mobile:
                st.markdown(f"""
                <div class="sms-container">
                    <span style="font-size: 1.5rem;">📲</span>
                    <div>
                        <b>SMS Notification:</b> Your EduPrep AI Login OTP for <b>{st.session_state.login_mobile}</b> is: 
                        <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: 3px; color: #DC2626; margin-left: 0.5rem;">{st.session_state.login_otp_code}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.form("login_verify_otp_form"):
                    otp_entered = st.text_input("🔢 Enter 4-Digit OTP", max_chars=4, placeholder="e.g. 1234")
                    verify_btn = st.form_submit_button("🔓 Verify OTP & Enter Dashboard (Press Enter)", type="primary", use_container_width=True)
                    
                    if verify_btn:
                        success, msg = sm.verify_otp(st.session_state.login_mobile, otp_entered)
                        if success:
                            student = sm.get_student_by_mobile(st.session_state.login_mobile)
                            st.session_state.logged_in_student = student
                            st.session_state.login_otp_sent = False
                            st.session_state.login_otp_code = None
                            st.success("✅ Login successful! Loading dashboard...")
                            st.rerun()
                        else:
                            st.error(msg)

        # --- TAB 2: REGISTER WITH MOBILE OTP ---
        with tab_register:
            st.markdown("#### New Student Registration")
            
            if not st.session_state.reg_otp_sent:
                with st.form("reg_step1_form"):
                    r_name = st.text_input("👤 Full Name", placeholder="e.g. Harsh Varma")
                    r_enroll = st.text_input("🆔 GTU Enrollment No.", placeholder="e.g. 210200107003")
                    r_mobile = st.text_input("📱 Mobile Number", placeholder="e.g. 9876543212")
                    
                    r_col_b, r_col_s = st.columns(2)
                    with r_col_b:
                        r_branch = st.selectbox("Branch", ["Computer Engineering", "Information Technology", "AI & Data Science", "Electronics & Comm.", "Mechanical Engg", "Civil Engg"])
                    with r_col_s:
                        r_sem = st.selectbox("Semester", ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"])

                    send_reg_otp = st.form_submit_button("📩 Send Verification OTP (Press Enter)", type="primary", use_container_width=True)
                    if send_reg_otp:
                        if not r_name or not r_enroll or not r_mobile:
                            st.warning("Please fill in all details!")
                        elif len(r_mobile.strip()) != 10 or not r_mobile.strip().isdigit():
                            st.warning("Please enter a valid 10-digit mobile number.")
                        elif sm.is_mobile_registered(r_mobile.strip()):
                            st.error("This mobile number is already registered.")
                        else:
                            otp = sm.generate_otp(r_mobile.strip())
                            st.session_state.reg_otp_sent = True
                            st.session_state.reg_otp_code = otp
                            st.session_state.reg_data = {
                                "name": r_name,
                                "enrollment_no": r_enroll,
                                "mobile_no": r_mobile.strip(),
                                "branch": r_branch,
                                "semester": r_sem
                            }
                            st.rerun()

            if st.session_state.reg_otp_sent:
                st.markdown(f"""
                <div class="sms-container">
                    <span style="font-size: 1.5rem;">📲</span>
                    <div>
                        <b>SMS Notification:</b> Your Registration OTP for <b>{st.session_state.reg_data.get('mobile_no')}</b> is: 
                        <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: 3px; color: #DC2626; margin-left: 0.5rem;">{st.session_state.reg_otp_code}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.form("reg_step2_form"):
                    reg_otp_entered = st.text_input("🔢 Enter 4-Digit OTP to Confirm", max_chars=4, placeholder="e.g. 1234")
                    col_reg_sub, col_reg_cancel = st.columns(2)
                    with col_reg_sub:
                        confirm_reg = st.form_submit_button("✅ Verify & Complete (Press Enter)", type="primary", use_container_width=True)
                    with col_reg_cancel:
                        cancel_reg = st.form_submit_button("Cancel", use_container_width=True)

                    if cancel_reg:
                        st.session_state.reg_otp_sent = False
                        st.rerun()

                    if confirm_reg:
                        d = st.session_state.reg_data
                        success, msg = sm.verify_otp(d["mobile_no"], reg_otp_entered)
                        if success:
                            ok, reg_msg, student_obj = sm.register_student(
                                d["mobile_no"], d["enrollment_no"], d["name"], d["branch"], d["semester"]
                            )
                            if ok:
                                st.session_state.logged_in_student = student_obj
                                st.session_state.reg_otp_sent = False
                                st.session_state.reg_otp_code = None
                                st.session_state.reg_data = {}
                                st.success("Registration complete! Logging in...")
                                st.rerun()
                            else:
                                st.error(reg_msg)
                        else:
                            st.error(msg)

        # --- TAB 3: ADMIN LOGIN GATEWAY ---
        with tab_admin_login:
            st.markdown("#### 🛡️ University Administrator Access")
            st.caption("Secure login for university controllers, faculty, and examiners.")
            
            with st.form("admin_access_form"):
                admin_pin = st.text_input("🔑 Admin Master Password / PIN", type="password", placeholder="Enter Admin Pin (e.g. admin123)")
                submit_admin = st.form_submit_button("🛡️ Access Admin Control Center (Press Enter)", type="primary", use_container_width=True)
                
                if submit_admin:
                    if admin_pin.strip() in ["admin123", "gtu2026", "admin"]:
                        st.session_state.is_admin = True
                        st.success("Admin identity verified! Loading Admin Control Center...")
                        st.rerun()
                    else:
                        st.error("Invalid Admin PIN. (Default demo PIN: admin123)")

        st.divider()
        st.info("💡 **Pre-configured Viva Demo Accounts:**  \n- Mobile: `9876543210` (Rahul Patel - Sem 7 CE)  \n- Mobile: `9876543211` (Priya Sharma - Sem 7 IT)  \n- 🛡️ Admin Password: `admin123`")

# ==============================================================================
# VIEW 3: AUTHENTICATED STUDENT SUITE (When Student is Logged In)
# ==============================================================================
else:
    curr_student = st.session_state.logged_in_student
    
    with st.sidebar:
        st.markdown(f"""
        <div class="student-id-card">
            <div class="id-header">
                <span class="id-chip">🎓 GTU VERIFIED</span>
                <span class="status-dot">🟢 ACTIVE</span>
            </div>
            <div class="id-name">👤 {curr_student['name']}</div>
            <div class="id-meta"><b>🆔 GTU ID:</b> {curr_student['enrollment_no']}</div>
            <div class="id-meta"><b>📱 Mobile:</b> +91 {curr_student['mobile_no']}</div>
            <div class="id-meta"><b>🏫 Branch:</b> {curr_student['branch']} ({curr_student['semester']})</div>
            <div style="font-family: monospace; letter-spacing: 4px; font-size: 0.7rem; color: rgba(255, 255, 255, 0.4); margin-top: 0.8rem; border-top: 1px dashed rgba(255, 255, 255, 0.2); padding-top: 0.5rem;">||| | |||| | ||| || |||| | ||</div>
        </div>
        """, unsafe_allow_html=True)

        col_side_out, col_side_adm = st.columns(2)
        with col_side_out:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in_student = None
                st.session_state.rag_engine = None
                st.session_state.indexed = False
                st.rerun()
        with col_side_adm:
            if st.button("🛡️ Admin Mode", use_container_width=True):
                st.session_state.is_admin = True
                st.rerun()

        st.divider()

        saved_key = os.getenv("GEMINI_API_KEY", "").strip()
        if saved_key:
            st.success("🔒 **Gemini AI Key: Connected**")
            api_key = saved_key
            with st.expander("⚙️ Manage AI API Key"):
                with st.form("sidebar_key_form"):
                    edit_key = st.text_input("Update Key", value=saved_key, type="password")
                    if st.form_submit_button("Save Changes"):
                        save_api_key_to_env(edit_key)
                        st.rerun()
        else:
            with st.form("sidebar_input_key_form"):
                api_key_input = st.text_input("🔑 Gemini API Key", type="password")
                if st.form_submit_button("Save API Key"):
                    if api_key_input:
                        save_api_key_to_env(api_key_input)
                        st.rerun()
            api_key = ""

        st.divider()

        st.subheader(f"📚 Course Knowledge Base")
        uploaded_files = st.file_uploader(
            "Upload Syllabus / Notes (PDF)",
            type=["pdf"],
            accept_multiple_files=True
        )

        col_load, col_sample = st.columns(2)
        with col_load:
            process_btn = st.button("⚡ Index Notes", use_container_width=True, type="primary")
        with col_sample:
            load_sample_btn = st.button("📖 Sample Notes", use_container_width=True, help="Load built-in AI/ML GTU notes")

        sample_pdf_path = os.path.join(os.path.dirname(__file__), "sample_notes", "AI_Machine_Learning_GTU_Notes.pdf")
        if load_sample_btn:
            if not api_key:
                st.error("Please provide Gemini API Key!")
            elif os.path.exists(sample_pdf_path):
                with st.spinner("Indexing sample notes..."):
                    engine = RAGEngine(api_key=api_key)
                    pages = engine.extract_text_from_pdfs([sample_pdf_path])
                    chunks = engine.split_into_chunks(pages)
                    engine.build_vector_index(chunks)
                    
                    st.session_state.rag_engine = engine
                    st.session_state.indexed = True
                    st.session_state.stats = {"chunks": len(chunks), "pages": len(pages), "files": 1}
                    st.success("✅ Sample Notes loaded!")
                    st.rerun()

        if process_btn:
            if not api_key:
                st.error("Please enter Gemini API Key!")
            elif not uploaded_files:
                st.warning("Please upload at least one PDF file!")
            else:
                with st.spinner("Processing & indexing notes..."):
                    try:
                        student_dir = sm.get_student_folder(curr_student["mobile_no"])
                        saved_paths = []
                        for uf in uploaded_files:
                            fpath = os.path.join(student_dir, uf.name)
                            with open(fpath, "wb") as f_out:
                                f_out.write(uf.getbuffer())
                            saved_paths.append(fpath)

                        engine = RAGEngine(api_key=api_key)
                        pages = engine.extract_text_from_pdfs(saved_paths)
                        chunks = engine.split_into_chunks(pages)
                        engine.build_vector_index(chunks)

                        st.session_state.rag_engine = engine
                        st.session_state.indexed = True
                        st.session_state.stats = {
                            "chunks": len(chunks),
                            "pages": len(pages),
                            "files": len(saved_paths)
                        }
                        st.success(f"✅ Indexed {len(chunks)} chunks!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.indexed:
            st.divider()
            st.subheader("📊 Knowledge Base Stats")
            s1, s2, s3 = st.columns(3)
            s1.metric("Files", st.session_state.stats["files"])
            s2.metric("Pages", st.session_state.stats["pages"])
            s3.metric("Chunks", st.session_state.stats["chunks"])

    # --- LIVE UNIVERSITY NOTICE BANNER (If Active) ---
    student_notices = sm.get_active_announcements(branch=curr_student["branch"])
    if student_notices:
        latest = student_notices[0]
        st.markdown(f"""
        <div class="notice-card">
            <b>📢 Official University Notice ({latest['priority']}):</b> {latest['title']}
            <div style="font-size: 0.9rem; color: #92400E; margin-top: 0.2rem;">{latest['message']}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- HERO DASHBOARD BANNER ---
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-badge">⚡ GTU 15-DAYS INTERNSHIP AI SUITE</div>
        <div class="hero-title">EduPrep <span class="gradient-text">AI Suite</span></div>
        <div class="hero-subtitle">Active Scholar: <b>{curr_student['name']}</b> | GTU ID: <b>{curr_student['enrollment_no']}</b> | {curr_student['branch']}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "💬 Multilingual Q&A & Voice",
        "🎙️ AI Mock Viva Examiner",
        "🎴 3D Digital Flashcards",
        "📸 Handwritten Notes Scanner",
        "📊 GTU Syllabus Audit",
        "🧠 Interactive MCQ Quiz",
        "📝 GTU Exam Paper",
        "🏆 Certificate & Performance"
    ])

    # ----------------- TAB 1: MULTILINGUAL CHAT & AUDIO -----------------
    with tab1:
        st.markdown("### 💬 Multilingual Academic Q&A & Voice Explainer")
        st.caption("Ask questions in English, Gujarati (ગુજરાતી), or Hindi (हिन्दी) with natural voice audio playback.")
        
        chat_history = sm.get_chat_history(curr_student["mobile_no"])
        
        col_lang, col_clear = st.columns([3, 1])
        with col_lang:
            selected_lang = st.radio(
                "Select Output Language:",
                ["English", "Gujarati (ગુજરાતી)", "Hindi (हिन्दी)"],
                horizontal=True
            )
        with col_clear:
            if chat_history and st.button("🧹 Clear History", use_container_width=True):
                sm.clear_chat_history(curr_student["mobile_no"])
                st.rerun()

        if not st.session_state.indexed:
            st.info("👈 **Get Started**: Click **Load Sample** or upload your course PDFs in the sidebar.")
        else:
            st.markdown("**Quick Interactive Topics:**")
            chip_col1, chip_col2, chip_col3 = st.columns(3)
            with chip_col1:
                if st.button("💡 Supervised vs Unsupervised"):
                    st.session_state.current_prompt = "Differentiate between Supervised and Unsupervised Learning with examples."
            with chip_col2:
                if st.button("💡 Overfitting & Prevention"):
                    st.session_state.current_prompt = "What is Overfitting in Machine Learning and how to prevent it?"
            with chip_col3:
                if st.button("💡 Decision Trees"):
                    st.session_state.current_prompt = "Explain Decision Tree algorithm with entropy and information gain."

            for msg in chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if "citations" in msg and msg["citations"]:
                        with st.expander("🔍 View Source Citations & References"):
                            for cite in msg["citations"]:
                                st.markdown(f"**📄 {cite['source']} (Page {cite['page']})**")
                                st.markdown(f"_{cite['snippet']}_")

            user_input = st.chat_input("Ask any academic concept, formula, or GTU topic... (Press Enter)")
            
            if "current_prompt" in st.session_state and st.session_state.current_prompt:
                user_input = st.session_state.current_prompt
                st.session_state.current_prompt = None

            if user_input:
                if not st.session_state.rag_engine:
                    st.error("Please index notes from the sidebar first!")
                else:
                    if api_key:
                        st.session_state.rag_engine.set_api_key(api_key)
                        
                    sm.save_chat_message(curr_student["mobile_no"], "user", user_input)
                    with st.chat_message("user"):
                        st.markdown(user_input)

                    with st.chat_message("assistant"):
                        with st.spinner(f"Synthesizing answer in {selected_lang}..."):
                            try:
                                res = st.session_state.rag_engine.query_multilingual(user_input, language=selected_lang)
                                answer = res["answer"]
                                citations = res["citations"]
                                
                                st.markdown(answer)
                                
                                try:
                                    audio_bytes = st.session_state.rag_engine.generate_audio_speech(answer, language=selected_lang)
                                    st.audio(audio_bytes, format="audio/mp3")
                                except Exception as e:
                                    st.caption(f"Audio note: {e}")

                                if citations:
                                    with st.expander("🔍 View Source Citations & References"):
                                        for cite in citations:
                                            st.markdown(f"**📄 {cite['source']} (Page {cite['page']})**")
                                            st.markdown(f"_{cite['snippet']}_")
                                            
                                sm.save_chat_message(curr_student["mobile_no"], "assistant", answer, citations)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating answer: {str(e)}")

    # ----------------- TAB 2: AI MOCK VIVA EXAMINER -----------------
    with tab2:
        st.markdown("### 🎙️ AI Mock Viva Examiner (GTU 30-Marks Assessment)")
        st.caption("Experience a realistic external viva interview based on your indexed course notes.")

        if not st.session_state.indexed:
            st.info("👈 Please index your study material from the sidebar first.")
        else:
            if not st.session_state.viva_questions:
                if st.button("🚀 Start New Mock Viva Interview (5 Questions)", type="primary"):
                    with st.spinner("Senior GTU Examiner is preparing your viva questions..."):
                        try:
                            if api_key:
                                st.session_state.rag_engine.set_api_key(api_key)
                            qs = st.session_state.rag_engine.generate_viva_questions(num_questions=5)
                            st.session_state.viva_questions = qs
                            st.session_state.viva_answers = {}
                            st.session_state.viva_result = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error starting viva: {e}")

            if st.session_state.viva_questions:
                st.markdown("""
                <div class="examiner-box">
                    <div class="examiner-avatar">👨‍🏫 GTU Senior External Examiner</div>
                    <div>"Welcome, candidate! Answer the following 5 oral viva questions in your own words. Click 'Submit Viva for Evaluation' when finished."</div>
                </div>
                """, unsafe_allow_html=True)

                with st.form("viva_form"):
                    for idx, q in enumerate(st.session_state.viva_questions):
                        st.markdown(f"**Viva Question {idx + 1}:** {q}")
                        st.session_state.viva_answers[idx] = st.text_area(
                            f"Your Answer for Q{idx+1}:",
                            value=st.session_state.viva_answers.get(idx, ""),
                            key=f"viva_ans_{idx}",
                            placeholder="Type your explanation, formula, or approach here..."
                        )
                        st.divider()

                    submit_viva = st.form_submit_button("📊 Submit Viva for Evaluation (30 Marks)", type="primary")

                if submit_viva:
                    with st.spinner("GTU Examiner is grading your viva answers..."):
                        try:
                            transcript_lines = []
                            for idx, q in enumerate(st.session_state.viva_questions):
                                ans = st.session_state.viva_answers.get(idx, "No answer provided.")
                                transcript_lines.append(f"Q{idx+1}: {q}\nStudent's Answer: {ans}")
                            
                            full_transcript = "\n\n".join(transcript_lines)
                            eval_report = st.session_state.rag_engine.evaluate_viva_exam(
                                student_name=curr_student["name"],
                                branch=curr_student["branch"],
                                semester=curr_student["semester"],
                                transcript=full_transcript
                            )
                            st.session_state.viva_result = eval_report
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error evaluating viva: {e}")

            if st.session_state.viva_result:
                st.subheader("📋 Official GTU Viva Marksheet & Evaluation Report:")
                st.markdown(st.session_state.viva_result)
                if st.button("🔄 Start Fresh Viva"):
                    st.session_state.viva_questions = []
                    st.session_state.viva_result = None
                    st.rerun()

    # ----------------- TAB 3: DIGITAL FLASHCARDS -----------------
    with tab3:
        st.markdown("### 🎴 3D Digital Flashcards (Active Recall)")
        st.caption("Flip through high-yield concept and formula cards before exams.")

        if not st.session_state.indexed:
            st.info("👈 Please index your study material from the sidebar first.")
        else:
            if not st.session_state.flashcards_data:
                if st.button("⚡ Generate 8 Flashcards from Notes", type="primary"):
                    with st.spinner("Synthesizing revision flashcards..."):
                        try:
                            if api_key:
                                st.session_state.rag_engine.set_api_key(api_key)
                            cards = st.session_state.rag_engine.generate_flashcards(num_cards=8)
                            st.session_state.flashcards_data = cards
                            st.session_state.card_index = 0
                            st.session_state.card_flipped = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating flashcards: {e}")

            if st.session_state.flashcards_data:
                cards = st.session_state.flashcards_data
                idx = st.session_state.card_index
                curr_card = cards[idx]

                st.markdown(f"**Card {idx + 1} of {len(cards)}** | Category: `{curr_card.get('category', 'Core Concept')}`")
                
                if not st.session_state.card_flipped:
                    st.markdown(f"""
                    <div class="flashcard-wrapper">
                        <div style="font-size: 0.85rem; color: #6366F1; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.8rem;">[ FRONT • CONCEPT / QUESTION ]</div>
                        <div class="flashcard-front">{curr_card['front']}</div>
                        <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 1.2rem;">💡 Click 'Flip Card' below to reveal model explanation</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="flashcard-wrapper" style="border-color: #10B981; background: #F0FDF4;">
                        <div style="font-size: 0.85rem; color: #059669; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.8rem;">[ BACK • MODEL EXPLANATION & KEY POINTS ]</div>
                        <div class="flashcard-back">{curr_card['back']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                col_prev, col_flip, col_next = st.columns(3)
                with col_prev:
                    if st.button("⬅️ Previous Card", use_container_width=True):
                        st.session_state.card_index = (idx - 1) % len(cards)
                        st.session_state.card_flipped = False
                        st.rerun()
                with col_flip:
                    if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                        st.session_state.card_flipped = not st.session_state.card_flipped
                        st.rerun()
                with col_next:
                    if st.button("Next Card ➡️", use_container_width=True):
                        st.session_state.card_index = (idx + 1) % len(cards)
                        st.session_state.card_flipped = False
                        st.rerun()

    # ----------------- TAB 4: HANDWRITTEN NOTES SCANNER -----------------
    with tab4:
        st.markdown("### 📸 Handwritten Notes & Blackboard Diagram Scanner")
        st.caption("Upload photos of your class notebooks or blackboard diagrams for instant OCR & AI analysis.")

        uploaded_img = st.file_uploader(
            "Upload Notebook / Blackboard Image (JPG / PNG)",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Uploaded Notes Image", width=380)

            if st.button("🔍 Scan with Gemini Vision AI", type="primary"):
                if not api_key:
                    st.error("Please enter Gemini API Key in sidebar!")
                else:
                    with st.spinner("Transcribing handwriting & decoding diagrams..."):
                        try:
                            engine = st.session_state.rag_engine or RAGEngine(api_key=api_key)
                            img_bytes = uploaded_img.getvalue()
                            mime_type = uploaded_img.type or "image/jpeg"
                            
                            analysis = engine.scan_handwritten_notes_image(img_bytes, mime_type=mime_type)
                            st.session_state.rag_engine = engine
                            st.session_state.indexed = True
                            st.session_state.last_vision_analysis = analysis
                            st.success("✅ Handwritten notes transcribed and added to knowledge base!")
                        except Exception as e:
                            st.error(f"Vision error: {e}")

        if "last_vision_analysis" in st.session_state and st.session_state.last_vision_analysis:
            st.subheader("📝 Transcribed Text & Diagram Analysis:")
            st.markdown(st.session_state.last_vision_analysis)

    # ----------------- TAB 5: GTU SYLLABUS AUDIT -----------------
    with tab5:
        st.markdown("### 📊 GTU Syllabus Coverage & Missing Topic Audit")
        st.caption("Audit how much of the official GTU curriculum is covered in your notes and identify missing topics.")

        if not st.session_state.indexed:
            st.info("👈 Please index your study material from the sidebar first.")
        else:
            custom_syl = st.text_area(
                "Paste Specific GTU Module / Topic List (Optional):",
                placeholder="e.g. Unit 1: Problem Solving & Search, Unit 2: Supervised Learning, Unit 3: Decision Trees...",
                value="Standard GTU AI & Machine Learning Syllabus"
            )

            if st.button("🔍 Run Syllabus Coverage Audit", type="primary"):
                with st.spinner("Analyzing curriculum coverage and gaps..."):
                    try:
                        if api_key:
                            st.session_state.rag_engine.set_api_key(api_key)
                        audit_report = st.session_state.rag_engine.audit_syllabus_coverage(custom_syl)
                        st.session_state.syllabus_report = audit_report
                    except Exception as e:
                        st.error(f"Audit error: {e}")

            if "syllabus_report" in st.session_state and st.session_state.syllabus_report:
                st.markdown(st.session_state.syllabus_report)

    # ----------------- TAB 6: INTERACTIVE MCQ QUIZ -----------------
    with tab6:
        st.markdown(f"### 🧠 Interactive Self-Assessment MCQ Quiz ({curr_student['name']})")
        st.caption("Test your conceptual understanding. Scores are saved automatically to your profile.")
        
        if not st.session_state.indexed:
            st.info("👈 Please index your study material from the sidebar first.")
        else:
            q_col1, q_col2 = st.columns([1, 3])
            with q_col1:
                num_q = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
            with q_col2:
                gen_quiz_btn = st.button("🎲 Generate New Quiz", type="primary")

            if gen_quiz_btn:
                with st.spinner("Crafting MCQs from your notes..."):
                    try:
                        if api_key:
                            st.session_state.rag_engine.set_api_key(api_key)
                        st.session_state.quiz_data = st.session_state.rag_engine.generate_mcq_quiz(num_questions=num_q)
                        st.session_state.quiz_submitted = False
                        st.session_state.user_answers = {}
                    except Exception as e:
                        st.error(f"Error generating quiz: {e}")

            if st.session_state.quiz_data:
                st.divider()
                with st.form("quiz_form"):
                    for idx, q in enumerate(st.session_state.quiz_data):
                        st.markdown(f"**Q{idx + 1}. {q['question']}**")
                        selected = st.radio(
                            "Select your answer:",
                            q["options"],
                            key=f"quiz_opt_{idx}",
                            index=None
                        )
                        st.session_state.user_answers[idx] = selected
                        st.write("")

                    submit_quiz = st.form_submit_button("📊 Submit & Save Score", type="primary")

                if submit_quiz:
                    st.session_state.quiz_submitted = True
                    score = 0
                    total = len(st.session_state.quiz_data)
                    
                    for idx, q in enumerate(st.session_state.quiz_data):
                        user_ans = st.session_state.user_answers.get(idx)
                        correct_ans = q["options"][q["correct_index"]]
                        if user_ans == correct_ans:
                            score += 1

                    pct = (score / total) * 100
                    sm.save_quiz_result(curr_student["mobile_no"], score, total, topic="GTU Notes Self-Assessment")
                    
                    st.subheader(f"🎯 Your Score: {score} / {total} ({pct:.1f}%)")
                    st.progress(score / total)
                    
                    if pct >= 80:
                        st.balloons()
                        st.success("🌟 Excellent! Score recorded in your progress report.")
                    elif pct >= 50:
                        st.info("👍 Good effort! Review explanations below.")
                    else:
                        st.warning("⚠️ Needs Revision.")

                    st.divider()
                    st.subheader("📝 Answer Review & Explanations:")
                    for idx, q in enumerate(st.session_state.quiz_data):
                        user_ans = st.session_state.user_answers.get(idx)
                        correct_ans = q["options"][q["correct_index"]]
                        is_correct = (user_ans == correct_ans)
                        
                        with st.expander(f"Q{idx + 1}: {q['question']} {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                            st.markdown(f"**Your Answer:** {user_ans if user_ans else 'Not Answered'}")
                            st.markdown(f"**Correct Answer:** `{correct_ans}`")
                            st.markdown(f"**💡 Explanation:** {q.get('explanation', 'Refer to notes.')}")

    # ----------------- TAB 7: GTU EXAM PAPER GENERATOR -----------------
    with tab7:
        st.markdown("### 📝 GTU Question Paper & Model Answer Generator")
        st.caption("Generate exam questions matching GTU 3, 4, and 7 marks structure.")
        
        if not st.session_state.indexed:
            st.info("👈 Please index your study material from the sidebar first.")
        else:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                topic_focus = st.text_input("Topic Focus / Module (Optional)", value="All Covered Modules", placeholder="e.g. Unit 2: Supervised Learning")
            with col_t2:
                difficulty = st.selectbox("Exam Difficulty Level", ["Standard GTU University Exam Level", "Direct & Conceptual (Easy)", "Analytical & Application (Challenging)"])

            if st.button("🚀 Generate GTU Exam Paper", type="primary"):
                with st.spinner("Generating GTU 3/4/7 Marks Questions & Model Solutions..."):
                    try:
                        if api_key:
                            st.session_state.rag_engine.set_api_key(api_key)
                        paper_content = st.session_state.rag_engine.generate_gtu_paper(topic_focus, difficulty)
                        st.session_state.exam_paper = paper_content
                    except Exception as e:
                        st.error(f"Error: {e}")

            if "exam_paper" in st.session_state and st.session_state.exam_paper:
                st.markdown(st.session_state.exam_paper)
                st.download_button(
                    "📥 Download GTU Exam Paper (Markdown)",
                    data=st.session_state.exam_paper,
                    file_name=f"GTU_Exam_Paper_{curr_student['enrollment_no']}.md",
                    mime="text/markdown"
                )

    # ----------------- TAB 8: CERTIFICATE & PERFORMANCE CARD -----------------
    with tab8:
        st.markdown(f"### 🏆 Official GTU Study Certificate & Performance Report")
        st.caption(f"Candidate: {curr_student['name']} | GTU Enrollment: {curr_student['enrollment_no']} | {curr_student['branch']}")
        
        analytics = sm.get_student_quiz_analytics(curr_student["mobile_no"])
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{analytics['total_attempts']}</div>
                <div class="metric-lbl">Quizzes Completed</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #2563EB;">{analytics['average_score']:.1f}%</div>
                <div class="metric-lbl">Average Mastery</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #16A34A;">{analytics['highest_score']:.1f}%</div>
                <div class="metric-lbl">Highest Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()

        # PDF Certificate Download
        st.subheader("📄 Official Academic Certificate & Internship Report (PDF)")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FEFCE8 0%, #FEF9C3 100%); border: 2px dashed #EAB308; border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 1.6rem;">📜 🎓 ⭐</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #854D0E; margin-top: 0.5rem;">GTU Verified Academic Assessment Certificate</div>
            <div style="font-size: 0.9rem; color: #A16207;">Generated dynamically with your official Enrollment ID, verified score percentages, and topic competencies.</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            cert_pdf_bytes = generate_student_certificate_pdf(curr_student, analytics)
            st.download_button(
                "🎓 Download My Verified GTU Performance Certificate (PDF)",
                data=cert_pdf_bytes,
                file_name=f"GTU_Certificate_{curr_student['enrollment_no']}.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Error generating PDF certificate: {e}")

        st.divider()
        st.subheader("📋 Detailed Assessment History")
        if analytics["history"]:
            history_table = []
            for h in analytics["history"]:
                history_table.append({
                    "Date & Time": h["date"],
                    "Topic": h["topic"],
                    "Score": h["score"],
                    "Percentage (%)": f"{h['percentage']:.1f}%",
                    "Status": "✅ Mastered" if h["percentage"] >= 80 else ("👍 Passed" if h["percentage"] >= 50 else "⚠️ Needs Review")
                })
            st.dataframe(history_table, use_container_width=True)
        else:
            st.info("No quiz attempts recorded yet. Attempt a quiz in Tab 6 to populate your score record.")

