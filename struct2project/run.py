# run.py
import sys
from streamlit.web.cli import main

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "TK_GUI.py",  # Replace with your actual Streamlit python file name if different
        "--global.developmentMode=false",
    ]
    sys.exit(main())