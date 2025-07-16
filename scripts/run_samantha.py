#!/usr/bin/env python3
"""
Main entry point for Samantha AI
Run this script to start the complete Samantha AI system
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import the main app
from app import SamanthaAI

def main():
    """Main entry point"""
    try:
        # Initialize and run Samantha AI
        samantha = SamanthaAI()
        samantha.run()
        
    except KeyboardInterrupt:
        print("\nGoodbye! It was wonderful talking with you.")
        sys.exit(0)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please try refreshing the page or contact support if the problem persists.")

if __name__ == "__main__":
    main()
