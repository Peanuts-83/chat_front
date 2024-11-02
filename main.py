# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import customtkinter as ctk

from app_manager import AppManager



if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Appearance mode
    ctk.set_default_color_theme("blue")  # Default color theme
    app_manager = AppManager()