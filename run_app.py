#!/usr/bin/env python
"""
Entry point để chạy Trading Bot với AI chat mode
Chạy: python run_app.py
"""

import sys
import os

# Thêm src vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import và chạy app
from src.app import main

if __name__ == '__main__':
    main()

