import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, colorchooser, filedialog
import json
import os

class SettingsView:
    def __init__(self, app):
        self.app = app
        self.create_settings_tab()

    def create_settings_tab(self):
        # Settings tab content
        settings_frame = ttk.Frame(self.app.settings_tab, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            settings_frame, 
            text="⚙️ Settings", 
            font=("Helvetica", 16, "bold")
        )
        header.pack(pady=(0, 20))
        
        # Theme settings
        theme_frame = ttk.LabelFrame(settings_frame, text="Theme")
        theme_frame.pack(fill=tk.X, pady=10)
        
        theme_label = ttk.Label(theme_frame, text="Select Theme:")
        theme_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value=self.app.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame, 
            textvariable=self.theme_var, 
            values=self.app.themes,
            width=15,
            state="readonly"
        )
        theme_combo.pack(side=tk.LEFT, padx=10, pady=10)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Pomodoro settings
        pomodoro_frame = ttk.LabelFrame(settings_frame, text="🍅 Pomodoro Timer")
        pomodoro_frame.pack(fill=tk.X, pady=10)
        
        work_label = ttk.Label(pomodoro_frame, text="Work Duration (minutes):")
        work_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.work_duration = tk.StringVar(value=str(self.app.pomodoro_time // 60))
        work_entry = ttk.Entry(pomodoro_frame, textvariable=self.work_duration, width=5)
        work_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        break_label = ttk.Label(pomodoro_frame, text="Break Duration (minutes):")
        break_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.break_duration = tk.StringVar(value=str(self.app.break_time // 60))
        break_entry = ttk.Entry(pomodoro_frame, textvariable=self.break_duration, width=5)
        break_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Category management
        self.create_category_management_with_edit()
        
        # Save settings button
        save_button = ttk.Button(
            settings_frame,
            text="💾 Save Settings",
            command=self.save_all_settings,
            style="success.TButton"
        )
        save_button.pack(pady=20)

    def create_category_management_with_edit(self):
        # Frame for category management
        category_frame = ttk.LabelFrame(self.app.settings_tab, text="📁 Manage Categories")
        category_frame.pack(fill=tk.X, pady=10)

        # Listbox to display categories
        self.category_listbox = tk.Listbox(category_frame, height=5, font=("Helvetica", 10))
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate the listbox with existing categories
        for category in self.app.categories:
            self.category_listbox.insert(tk.END, category)

        # Buttons for adding, editing, and removing categories
        button_frame = ttk.Frame(category_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        add_button = ttk.Button(button_frame, text="➕ Add Category", command=self.add_category)
        add_button.pack(fill=tk.X, pady=5)

        edit_button = ttk.Button(button_frame, text="✏️ Edit Category", command=self.edit_category)
        edit_button.pack(fill=tk.X, pady=5)

        remove_button = ttk.Button(button_frame, text="❌ Remove Category", command=self.remove_category)
        remove_button.pack(fill=tk.X, pady=5)

    def add_category(self):
        new_category = simpledialog.askstring("Add Category", "Enter the new category name:")
        if new_category and new_category.strip():
            if new_category not in self.app.categories:
                self.app.categories.append(new_category)
                self.category_listbox.insert(tk.END, new_category)
                self.app.save_settings()
                messagebox.showinfo("Success", f"✅ Category '{new_category}' added successfully!")
            else:
                messagebox.showwarning("Warning", "⚠️ Category already exists!")

    def edit_category(self):
        try:
            selected_index = self.category_listbox.curselection()[0]
            current_category = self.app.categories[selected_index]
            new_category = simpledialog.askstring("Edit Category", f"Edit the category name (current: {current_category}):")
            if new_category and new_category.strip():
                if new_category not in self.app.categories:
                    self.app.categories[selected_index] = new_category
                    self.category_listbox.delete(selected_index)
                    self.category_listbox.insert(selected_index, new_category)
                    self.app.save_settings()
                    messagebox.showinfo("Success", f"✅ Category '{current_category}' updated to '{new_category}' successfully!")
                else:
                    messagebox.showwarning("Warning", "⚠️ Category already exists!")
        except IndexError:
            messagebox.showerror("Error", "⚠️ Please select a category to edit!")

    def remove_category(self):
        try:
            selected_index = self.category_listbox.curselection()[0]
            category_to_remove = self.app.categories[selected_index]
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove the category '{category_to_remove}'?")
            if confirm:
                self.app.categories.pop(selected_index)
                self.category_listbox.delete(selected_index)
                self.app.save_settings()
                messagebox.showinfo("Success", f"✅ Category '{category_to_remove}' removed successfully!")
        except IndexError:
            messagebox.showerror("Error", "⚠️ Please select a category to remove!")

    def change_theme(self, event=None):
        new_theme = self.theme_var.get()
        if new_theme != self.app.current_theme:
            self.app.current_theme = new_theme
            self.app.style.theme_use(new_theme)
            self.app.save_settings()

    def save_all_settings(self):
        try:
            # Update pomodoro times from input fields
            self.app.pomodoro_time = int(self.work_duration.get()) * 60
            self.app.break_time = int(self.break_duration.get()) * 60
            self.app.save_settings()
            messagebox.showinfo("Success", "✅ Settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "⚠️ Please enter valid numbers for Pomodoro durations!")
