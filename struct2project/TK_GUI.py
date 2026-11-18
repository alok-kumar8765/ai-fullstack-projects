import streamlit as st
from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Struct2Project Pro",
    page_icon="📂",
    layout="wide"
)

# --- TKINTER BROWSER HELPER (Runs locally on user's machine) ---
def browse_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Bring dialog to front
    folder_path = filedialog.askdirectory(title="Select Target Project Directory")
    root.destroy()
    return folder_path

# --- DEFAULT TEMPLATES & BOILERPLATE ---
django_template = """my_django_project/ # Main Django Project
├── manage.py
├── requirements.txt
├── my_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core_app/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    └── urls.py"""

# Standard boilerplate code dictionary for common files
BOILERPLATE_CODES = {
    "manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    "settings.py": """from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-me-in-production'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = 'static/'
""",
    "urls.py": """from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
""",
    "wsgi.py": """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')

application = get_wsgi_application()
"""
}

# --- SESSION STATE INITIALIZATION ---
if "target_dir" not in st.session_state:
    st.session_state["target_dir"] = str(Path.cwd() / "my_new_project")

# --- UI HEADER ---
st.title("📂 Struct2Project Pro: Markdown to Local Project Generator")
st.markdown("Generate full folder structures and standard boilerplate code directly on your local drive from Markdown or uploaded files!")

# --- SIDEBAR OPTIONS ---
st.sidebar.markdown("### ⚙️ Configuration & Templates")
template_choice = st.sidebar.selectbox("Load Sample Template", ["Custom", "Django Standard Project"])

default_text = ""
if template_choice == "Django Standard Project":
    default_text = django_template

# --- TARGET DIRECTORY BROWSER SECTION ---
st.markdown("### 📁 Select Target Directory")
col_path1, col_path2 = st.columns([4, 1])

with col_path1:
    target_path = st.text_input("Target Directory Path", value=st.session_state["target_dir"], label_visibility="collapsed")
with col_path2:
    if st.button("🔍 Browse Folder"):
        selected_dir = browse_folder()
        if selected_dir:
            st.session_state["target_dir"] = selected_dir
            st.rerun()

st.markdown("---")

# --- INPUT METHOD: TEXT AREA OR FILE UPLOAD ---
tab1, tab2 = st.tabs(["✍️ Paste Structure Text", "📁 Upload Structure File (.txt / .md)"])

raw_markdown_text = ""

with tab1:
    raw_markdown_text = st.text_area(
        "Paste Folder Structure (Markdown Tree)",
        value=default_text,
        height=250,
        placeholder="project_name/\n├── folder/\n│   └── file.py"
    )

with tab2:
    uploaded_file = st.file_uploader("Upload your structure file", type=["txt", "md"])
    if uploaded_file is not None:
        raw_markdown_text = uploaded_file.read().decode("utf-8")
        st.success(f"Successfully loaded structure from `{uploaded_file.name}`")
        with st.expander("👀 View Uploaded Content"):
            st.code(raw_markdown_text)

# --- PARSING & CREATION LOGIC ---
def parse_and_create_structure(raw_text, base_dir, add_boilerplate):
    lines = raw_text.strip().split("\n")
    base_path = Path(base_dir).resolve()
    
    path_stack = {}
    created_items = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Strip comments (Anything after '#' is a markdown comment, ignore it)
        if "#" in line:
            line = line.split("#")[0]
            
        if not line.strip():
            continue
            
        # Clean up tree characters like ├──, └──, │
        clean_line = line.replace("├──", "").replace("└──", "").replace("│", "").expandtabs(4)
        indent_level = len(clean_line) - len(clean_line.lstrip())
        item_name = clean_line.strip()
        
        if not item_name:
            continue
            
        is_directory = item_name.endswith("/") or "." not in item_name
        item_name = item_name.rstrip("/").strip()
        
        # Determine parent directory based on indentation
        levels_to_remove = [lvl for lvl in path_stack if lvl >= indent_level]
        for lvl in levels_to_remove:
            del path_stack[lvl]
            
        parent_path = base_path
        if path_stack:
            max_lvl = max(path_stack.keys())
            if max_lvl < indent_level:
                parent_path = path_stack[max_lvl]
                
        current_path = parent_path / item_name
        
        if is_directory:
            current_path.mkdir(parents=True, exist_ok=True)
            path_stack[indent_level] = current_path
            created_items.append(f"📁 Created Directory: {current_path}")
        else:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if boilerplate code should be added for standard files
            file_content = ""
            if add_boilerplate and item_name in BOILERPLATE_CODES:
                file_content = BOILERPLATE_CODES[item_name]
                
            if not current_path.exists():
                with open(current_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                if file_content:
                    created_items.append(f"📄 Created File with Boilerplate: {current_path}")
                else:
                    created_items.append(f"📄 Created File: {current_path}")
            else:
                created_items.append(f"⚠️ File already exists: {current_path}")
                
    return created_items

# --- EXECUTION BUTTON ---
add_boilerplate_toggle = st.checkbox("Automatically write standard boilerplate code for Django files (settings.py, urls.py, etc.)", value=True)

if st.button("🚀 Generate Project on Selected Drive", type="primary"):
    if not raw_markdown_text.strip():
        st.error("Please provide or upload a folder structure text!")
    elif not target_path.strip():
        st.error("Please provide a valid target directory path!")
    else:
        try:
            with st.spinner("Creating folders, files, and writing boilerplate code..."):
                results = parse_and_create_structure(raw_markdown_text, target_path.strip(), add_boilerplate_toggle)
            
            st.success("🎉 Project structure generated successfully on your local drive!")
            st.markdown("### 📋 Generation Log:")
            for res in results:
                st.code(res)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")