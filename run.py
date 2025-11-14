#!/usr/bin/env python
"""
Entry point chính để chạy Trading Bot
Chạy: python run.py
"""

import sys
import os

# Thêm src vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import và chạy main
from src.main import main

if __name__ == '__main__':
    main()

