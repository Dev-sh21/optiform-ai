import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit.web.cli as stcli

def handler(event, context):
    # This function is the entry point for Vercel serverless
    # However, Streamlit usually needs to be run as a process.
    # On Vercel, we can try to trigger the CLI.
    sys.argv = [
        "streamlit",
        "run",
        "optiform_ai/dashboard/app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0"
    ]
    stcli.main()
