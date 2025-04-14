import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import time
import datetime

class TaskView:
    def __init__(self, app):
        self.app = app
        self.create_tasks_tab()
    
    def create_tasks_tab(self):
        # Main frame
        main_frame = ttk.Frame(self.app.tasks_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top control frame
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # View mode selector
        view_label = ttk.Label(top_frame, text="View:")
        view_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.view_var = tk.StringVar(value=self.app.view_mode)
        view_combo = ttk.Combobox(
            top_frame, 
            textvariable=self.view_var, 
            values=["list", "kanban"],
            width=10,
            state="readonly"
        )
        view_combo.pack(side=tk.LEFT, padx=(0, 10))
        view_combo.bind("<<ComboboxSelected>>", self.change_view_mode)
        
        # Filter by category
        cat_label = ttk.Label(top_frame, text="Category:")
        cat_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.category_filter = tk.StringVar(value="All")
        cat_combo = ttk.Combobox(
            top_frame, 
            textvariable=self.category_filter, 
            values=["All"] + self.app.categories,
            width=12,
            state="readonly"
        )
        cat_combo.pack(side=tk.LEFT, padx=(0, 10))
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self.update_task_list())
        
        # Pomodoro timer button
        self.timer_var = tk.StringVar(value="🍅 Start Timer")
        timer_button = ttk.Button(
            top_frame,
            textvariable=self.timer_var,
            command=self.toggle_pomodoro,
            style="info.TButton"
        )
        timer_button.pack(side=tk.RIGHT, padx=5)
        
        # Task input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Task entry
        self.task_var = tk.StringVar()
        task_entry = ttk.Entry(
            input_frame,
            textvariable=self.task_var,
            font=("Helvetica", 12),
            width=30
        )
        task_entry.pack(side=tk.LEFT, padx=(0, 5), ipady=3, expand=True, fill=tk.X)
        task_entry.bind("<Return>", lambda event: self.add_task())
        
        # Category dropdown
        self.category_var = tk.StringVar(value=self.app.categories[0])
        cat_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.category_var, 
            values=self.app.categories,
            width=12,
            state="readonly"
        )
        cat_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Priority dropdown
        self.priority_var = tk.StringVar(value=self.app.priority_levels[1])  # Medium by default
        prio_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.priority_var, 
            values=self.app.priority_levels,
            width=10,
            state="readonly"
        )
        prio_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Due date picker
        self.due_date_var = tk.StringVar(value="No Date")
        due_date_button = ttk.Button(
            input_frame,
            text="📅 Due Date",
            command=self.pick_due_date
        )
        due_date_button.pack(side=tk.LEFT, padx=5)
        
        # Add task button
        self.add_button = ttk.Button(
            input_frame,
            text="Add Task",
            command=self.add_task,
            style="success.TButton"
        )
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Create container for different views
        self.view_container = ttk.Frame(main_frame)
        self.view_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize the list view (default)
        self.create_list_view()
        
        # Button frame at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Remove task button
        self.remove_button = ttk.Button(
            button_frame,
            text="Remove Task",
            command=self.remove_task,
            style="danger.TButton"
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        # Mark as complete button
        self.complete_button = ttk.Button(
            button_frame,
            text="Toggle Complete",
            command=self.toggle_complete,
            style="info.TButton"
        )
        self.complete_button.pack(side=tk.LEFT, padx=5)
        
        # Edit task button
        self.edit_button = ttk.Button(
            button_frame,
            text="Edit Task",
            command=self.edit_task,
            style="warning.TButton"
        )
        self.edit_button.pack(side=tk.LEFT, padx=5)
    
    def create_list_view(self):
        # Clear the view container
        for widget in self.view_container.winfo_children():
            widget.destroy()
        
        # Create a frame for the list view
        list_frame = ttk.Frame(self.view_container)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for tasks
        self.task_tree = ttk.Treeview(
            list_frame,
            columns=("Status", "Task", "Category", "Priority", "Due Date"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        
        # Define headings
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Category", text="Category")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Due Date", text="Due Date")
        
        # Define columns
        self.task_tree.column("Status", width=50, anchor="center")
        self.task_tree.column("Task", width=300, anchor="w")
        self.task_tree.column("Category", width=100, anchor="center")
        self.task_tree.column("Priority", width=80, anchor="center")
        self.task_tree.column("Due Date", width=100, anchor="center")
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_tree.yview)
        
        # Populate the treeview
        self.update_task_list()
    
    def create_kanban_view(self):
        # Clear the view container
        for widget in self.view_container.winfo_children():
            widget.destroy()
        
        # Create a frame for the kanban view with horizontal scrolling
        kanban_frame = ttk.Frame(self.view_container)
        kanban_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create columns based on status
        statuses = ["To Do", "In Progress", "Done"]
        
        for i, status in enumerate(statuses):
            column_frame = ttk.LabelFrame(kanban_frame, text=status)
            column_frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            
            # Make columns expandable
            kanban_frame.columnconfigure(i, weight=1)
            
            # Create scrollable task list for this column
            task_frame = ttk.Frame(column_frame)
            task_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Add tasks to this column
            filtered_tasks = []
            if status == "To Do":
                filtered_tasks = [t for t in self.app.tasks if not t.get("completed", False) and not t.get("in_progress", False)]
            elif status == "In Progress":
                filtered_tasks = [t for t in self.app.tasks if t.get("in_progress", False) and not t.get("completed", False)]
            elif status == "Done":
                filtered_tasks = [t for t in self.app.tasks if t.get("completed", False)]
            
            for task in filtered_tasks:
                task_card = ttk.Frame(task_frame, relief="raised", borderwidth=1)
                task_card.pack(fill=tk.X, pady=5, padx=2)
                
                # Priority indicator (colored bar on left)
                priority_color = self.get_priority_color(task.get("priority", "Medium"))
                priority_bar = tk.Frame(task_card, bg=priority_color, width=5)
                priority_bar.pack(side=tk.LEFT, fill=tk.Y)
                
                # Task content
                content = ttk.Frame(task_card)
                content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                name_label = ttk.Label(content, text=task["name"], wraplength=200)
                name_label.pack(anchor="w")
                
                details = f"{task.get('category', 'None')} • {task.get('priority', 'Medium')}"
                if task.get("due_date", "No Date") != "No Date":
                    details += f" • Due: {task.get('due_date')}"
                
                details_label = ttk.Label(content, text=details, foreground="gray")
                details_label.pack(anchor="w")
    
    def change_view_mode(self, event=None):
        new_mode = self.view_var.get()
        if new_mode != self.app.view_mode:
            self.app.view_mode = new_mode
            if new_mode == "list":
                self.create_list_view()
            elif new_mode == "kanban":
                self.create_kanban_view()
    
    def pick_due_date(self):
        # Simple due date picker using calendar dialog
        date_str = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD) or 'No Date':")
        if date_str:
            self.due_date_var.set(date_str)
    
    def toggle_pomodoro(self):
        if not self.app.timer_running:
            self.app.timer_running = True
            self.timer_var.set("🍅 Stop Timer")
            self.app.pomodoro_active = True
            threading.Thread(target=self.run_pomodoro_timer, daemon=True).start()
        else:
            self.app.timer_running = False
            self.timer_var.set("🍅 Start Timer")
    
    def run_pomodoro_timer(self):
        remaining_time = self.app.pomodoro_time
        while self.app.timer_running and remaining_time > 0:
            mins, secs = divmod(remaining_time, 60)
            time_str = f"🍅 {mins:02d}:{secs:02d}"
            self.timer_var.set(time_str)
            time.sleep(1)
            remaining_time -= 1
        
        if self.app.timer_running:
            # Timer completed
            self.app.timer_running = False
            messagebox.showinfo("Pomodoro", "✅ Work session completed! Take a break.")
            self.timer_var.set("🍅 Start Timer")
    
    def add_task(self):
        task_name = self.task_var.get().strip()
        if task_name:
            new_task = {
                "name": task_name,
                "category": self.category_var.get(),
                "priority": self.priority_var.get(),
                "due_date": self.due_date_var.get(),
                "completed": False,
                "in_progress": False,
                "created_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            self.app.tasks.append(new_task)
            self.update_task_list()
            self.app.save_tasks()
            self.task_var.set("")  # Clear the entry
            self.due_date_var.set("No Date")  # Reset due date
            
            # Show success message
            messagebox.showinfo("Success", "🎉 Task added successfully!")
        else:
            messagebox.showwarning("Warning", "⚠️ Please enter a task!")
    
    def update_task_list(self):
        if hasattr(self, 'task_tree'):
            # Clear the current list
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            
            # Filter tasks based on category
            filtered_tasks = self.app.tasks
            if self.category_filter.get() != "All":
                filtered_tasks = [t for t in filtered_tasks if t.get("category") == self.category_filter.get()]
            
            # Add filtered tasks to the tree
            for task in filtered_tasks:
                status = "✅" if task.get("completed", False) else "⬜"
                if task.get("in_progress", False) and not task.get("completed", False):
                    status = "🔄"
                
                self.task_tree.insert("", "end", values=(
                    status,
                    task["name"],
                    task.get("category", ""),
                    task.get("priority", ""),
                    task.get("due_date", "No Date")
                ))
            
            self.app.update_status()
    
    def toggle_complete(self):
        try:
            selected_item = self.task_tree.selection()[0]
            task_name = self.task_tree.item(selected_item)['values'][1]
            
            # Find the task in the list
            for task in self.app.tasks:
                if task["name"] == task_name:
                    task["completed"] = not task.get("completed", False)
                    if task["completed"]:
                        task["in_progress"] = False
                    break
            
            self.update_task_list()
            self.app.save_tasks()
        except (IndexError, KeyError):
            messagebox.showerror("Error", "⚠️ Please select a task!")
    
    def edit_task(self):
        try:
            selected_item = self.task_tree.selection()[0]
            task_name = self.task_tree.item(selected_item)['values'][1]
            
            # Find the task in the list
            for task in self.app.tasks:
                if task["name"] == task_name:
                    # Create a dialog to edit the task
                    edit_window = tk.Toplevel(self.app.root)
                    edit_window.title("Edit Task")
                    edit_window.geometry("400x300")
                    edit_window.resizable(False, False)
                    
                    # Task name
                    name_frame = ttk.Frame(edit_window)
                    name_frame.pack(fill=tk.X, padx=20, pady=10)
                    
                    name_label = ttk.Label(name_frame, text="Task Name:")
                    name_label.pack(anchor="w")
                    
                    name_var = tk.StringVar(value=task["name"])
                    name_entry = ttk.Entry(name_frame, textvariable=name_var, width=40)
                    name_entry.pack(fill=tk.X, pady=5)
                    
                    # Category
                    cat_frame = ttk.Frame(edit_window)
                    cat_frame.pack(fill=tk.X, padx=20, pady=10)
                    
                    cat_label = ttk.Label(cat_frame, text="Category:")
                    cat_label.pack(anchor="w")
                    
                    cat_var = tk.StringVar(value=task.get("category", self.app.categories[0]))
                    cat_combo = ttk.Combobox(cat_frame, textvariable=cat_var, values=self.app.categories, state="readonly")
                    cat_combo.pack(fill=tk.X, pady=5)
                    
                    # Priority
                    prio_frame = ttk.Frame(edit_window)
                    prio_frame.pack(fill=tk.X, padx=20, pady=10)
                    
                    prio_label = ttk.Label(prio_frame, text="Priority:")
                    prio_label.pack(anchor="w")
                    
                    prio_var = tk.StringVar(value=task.get("priority", "Medium"))
                    prio_combo = ttk.Combobox(prio_frame, textvariable=prio_var, values=self.app.priority_levels, state="readonly")
                    prio_combo.pack(fill=tk.X, pady=5)
                    
                    # Due date
                    date_frame = ttk.Frame(edit_window)
                    date_frame.pack(fill=tk.X, padx=20, pady=10)
                    
                    date_label = ttk.Label(date_frame, text="Due Date (YYYY-MM-DD):")
                    date_label.pack(anchor="w")
                    
                    date_var = tk.StringVar(value=task.get("due_date", "No Date"))
                    date_entry = ttk.Entry(date_frame, textvariable=date_var, width=20)
                    date_entry.pack(fill=tk.X, pady=5)
                    
                    # Save button
                    save_button = ttk.Button(
                        edit_window,
                        text="Save Changes",
                        command=lambda: self.save_task_edits(task, name_var, cat_var, prio_var, date_var, edit_window)
                    )
                    save_button.pack(pady=20)
                    
                    break
        except (IndexError, KeyError):
            messagebox.showerror("Error", "⚠️ Please select a task!")
    
    def save_task_edits(self, task, name_var, cat_var, prio_var, date_var, edit_window):
        task["name"] = name_var.get()
        task["category"] = cat_var.get()
        task["priority"] = prio_var.get()
        task["due_date"] = date_var.get()
        
        self.update_task_list()
        self.app.save_tasks()
        edit_window.destroy()
        messagebox.showinfo("Success", "✅ Task updated successfully!")

    def remove_task(self):
        try:
            selected_item = self.task_tree.selection()[0]
            task_name = self.task_tree.item(selected_item)['values'][1]
            
            # Find and remove the task
            for i, task in enumerate(self.app.tasks):
                if task["name"] == task_name:
                    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove '{task_name}'?")
                    if confirm:
                        self.app.tasks.pop(i)
                        self.update_task_list()
                        self.app.save_tasks()
                        messagebox.showinfo("Success", "❌ Task removed successfully!")
                    break
        except (IndexError, KeyError):
            messagebox.showerror("Error", "⚠️ Please select a task!")

    def get_priority_color(self, priority):
        if priority == "Low":
            return "#3CB371"  # Medium sea green
        elif priority == "Medium":
            return "#1E90FF"  # Dodger blue
        elif priority == "High":
            return "#FF8C00"  # Dark orange
        elif priority == "Urgent":
            return "#DC143C"  # Crimson
        return "#1E90FF"  # Default blue

