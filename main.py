import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, colorchooser, filedialog
import json
import os
import datetime
import random
from ttkbootstrap import Style
import threading
import time

from task_view import TaskView
from settings_view import SettingsView
from stats_view import StatsView

class TodoListApp:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme="darkly")
        self.root.title("🚀 Enhanced To-Do List")
        self.root.geometry("800x700")
        
        # App state variables
        self.tasks = []
        self.current_theme = "darkly"
        self.themes = ["darkly", "superhero", "solar", "cosmo", "flatly", "litera"]
        self.categories = ["Work", "Personal", "Shopping", "Health", "Education"]
        self.priority_levels = ["Low", "Medium", "High", "Urgent"]
        self.view_mode = "list"  # Options: list, kanban
        self.pomodoro_active = False
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.break_time = 5 * 60  # 5 minutes in seconds
        self.timer_running = False
        
        # Initialize status_var here
        self.status_var = tk.StringVar()
        
        # Load data
        self.load_tasks()
        self.load_settings()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tasks_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tasks_tab, text="📝 Tasks")
        self.notebook.add(self.stats_tab, text="📊 Statistics")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Create views
        self.task_view = TaskView(self)
        self.stats_view = StatsView(self)
        self.settings_view = SettingsView(self)
        
        # Status bar
        self.update_status()
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(10, 5)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_status(self):
        completed = sum(1 for task in self.tasks if task.get("completed", False))
        total = len(self.tasks)
        self.status_var.set(f"📊 Tasks: {total} | Completed: {completed} | Remaining: {total - completed}")
    
    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)

    def load_tasks(self):
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", "r") as f:
                    self.tasks = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Could not load tasks: {str(e)}")
    
    def save_settings(self):
        settings = {
            "categories": self.categories,
            "theme": self.current_theme,
            "pomodoro_time": self.pomodoro_time,
            "break_time": self.break_time
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.categories = settings.get("categories", self.categories)
                    self.current_theme = settings.get("theme", self.current_theme)
                    self.pomodoro_time = settings.get("pomodoro_time", self.pomodoro_time)
                    self.break_time = settings.get("break_time", self.break_time)
        except Exception as e:
            messagebox.showerror("Error", f"⚠️ Could not load settings: {str(e)}")
    
    def on_closing(self):
        # Save settings and tasks before closing
        self.save_settings()
        self.save_tasks()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoListApp(root)
    root.mainloop()
