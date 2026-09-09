import os
import shutil
import zipfile

src_dir = r"C:\Users\admin\.gemini\antigravity\scratch\gtu_ai_academic_bot"
desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
dest_folder = os.path.join(desktop_dir, "GTU_AI_Internship_Complete_Project")
zip_output = os.path.join(desktop_dir, "GTU_AI_Internship_Complete_Project.zip")

# Remove old if exists
if os.path.exists(dest_folder):
    shutil.rmtree(dest_folder, ignore_errors=True)
if os.path.exists(zip_output):
    os.remove(zip_output)

# Exclude unnecessary temporary files
ignore_patterns = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "cloudflared.exe", "cloudflared-windows-amd64.exe",
    "*.log", "save_tool.py", "make_*.py", "update_*.py", "admin_*.py", "ui_*.py", "part*.py"
)

# Copy to Desktop clean folder
shutil.copytree(src_dir, dest_folder, ignore=ignore_patterns)

# Create high-compression ZIP file for 1-Click Google Drive Upload
with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(dest_folder):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dest_folder)
            zf.write(full_path, os.path.join("GTU_AI_Internship_Complete_Project", rel_path))

zip_size_mb = os.path.getsize(zip_output) / (1024 * 1024)

print(f"SUCCESS: Packaged complete project to:")
print(f"1. Desktop Folder: {dest_folder}")
print(f"2. Google Drive Ready ZIP: {zip_output} (Size: {zip_size_mb:.2f} MB)")
