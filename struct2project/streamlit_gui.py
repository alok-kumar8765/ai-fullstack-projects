import streamlit as st
from pathlib import Path
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Struct2Project Generator",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Markdown Folder Structure to Local Project Generator")
st.markdown("Paste your project folder structure in Markdown tree format below, and generate it instantly on your local machine!")

# --- DEFAULT TEMPLATE EXAMPLES ---
django_template = """my_django_project/
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

react_template = """my_react_app/
├── package.json
├── public/
│   ├── index.html
│   └── favicon.ico
└── src/
    ├── App.js
    ├── App.css
    ├── index.js
    └── components/
        ├── Header.jsx
        └── Footer.jsx"""

# --- SIDEBAR TEMPLATES ---
st.sidebar.markdown("### 📋 Quick Templates")
template_choice = st.sidebar.selectbox("Load Sample Structure", ["Custom", "Django Project", "React App"])

default_text = ""
if template_choice == "Django Project":
    default_text = django_template
elif template_choice == "React App":
    default_text = react_template

# --- MAIN UI INPUT ---
target_path = st.text_input("Target Directory Path (Where to create the project)", value="./my_new_project")

markdown_input = st.text_area(
    "Paste Folder Structure (Markdown Tree)",
    value=default_text,
    height=300,
    placeholder="project_name/\n├── folder/\n│   └── file.py"
)

# --- PARSING & GENERATION LOGIC ---
def parse_and_create_structure(raw_text, base_dir):
    lines = raw_text.strip().split("\n")
    base_path = Path(base_dir).resolve()
    
    # Track paths at different indentation levels
    path_stack = {}
    created_items = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Calculate indentation level (count spaces or tree symbols)
        # Clean up tree characters like ├──, └──, │
        clean_line = line.replace("├──", "").replace("└──", "").replace("│", "").expandtabs(4)
        indent_level = len(clean_line) - len(clean_line.lstrip())
        item_name = clean_line.strip()
        
        if not item_name:
            continue
            
        is_directory = item_name.endswith("/") or "." not in item_name
        item_name = item_name.rstrip("/")
        
        # Determine parent directory based on indentation
        # Remove stack items deeper or equal to current indent
        levels_to_remove = [lvl for lvl in path_stack if lvl >= indent_level]
        for lvl in levels_to_remove:
            del path_stack[lvl]
            
        # Find parent path
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
            if not current_path.exists():
                current_path.touch()
                created_items.append(f"📄 Created File: {current_path}")
            else:
                created_items.append(f"⚠️ File already exists: {current_path}")
                
    return created_items

if st.button("🚀 Generate Project on Local Drive", type="primary"):
    if not markdown_input.strip():
        st.error("Please provide a folder structure markdown text!")
    elif not target_path.strip():
        st.error("Please provide a target directory path!")
    else:
        try:
            with st.spinner("Generating folders and files..."):
                results = parse_and_create_structure(markdown_input, target_path.strip())
            
            st.success("🎉 Project structure generated successfully!")
            st.markdown("### 📋 Generation Log:")
            for res in results:
                st.code(res)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")