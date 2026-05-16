#!/usr/bin/env python3
"""
Quick start script for ROBERT UI.

Usage:
    python start.py
    
or from agent/ui/:
    python ../start_ui.py
"""

import sys
from pathlib import Path

# Ensure we can import UI modules
ui_path = Path(__file__).parent / "agent" / "ui"
if ui_path.exists():
    sys.path.insert(0, str(ui_path))

# Import and run app
try:
    from app import main
    main()
except ImportError as e:
    print(f"Error: Could not import UI modules: {e}")
    print("Make sure you are running this from the project root.")
    print("Or run: cd agent/ui && python app.py")
    sys.exit(1)
