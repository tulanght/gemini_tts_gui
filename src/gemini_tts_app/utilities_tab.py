# file-path: src/gemini_tts_app/utilities_tab.py
# version: 1.0
# last-updated: 2025-08-18
# description: Module placeholder cho tab Tiện ích.

import tkinter as tk
from tkinter import ttk

class UtilitiesTab(ttk.Frame):
    def __init__(self, parent, main_app_instance):
        super().__init__(parent, padding="10")
        self.main_app = main_app_instance

        self._create_widgets()

    def _create_widgets(self):
        """Tạo giao diện placeholder cho tab."""
        label = ttk.Label(
            self,
            text="Tab Tiện ích",
            font=("Segoe UI", 16, "bold")
        )
        label.pack(pady=20)

        info_label = ttk.Label(
            self,
            text="Nơi đây sẽ chứa các công cụ hữu ích trong các phiên bản tương lai.",
            justify="center",
            wraplength=400
        )
        info_label.pack(pady=10)