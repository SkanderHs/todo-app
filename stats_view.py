import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set matplotlib backend for Tkinter
plt.switch_backend('Agg') 

class StatsView:
    def __init__(self, app):
        self.app = app
        self.create_stats_tab()

    def create_stats_tab(self):
        # Stats tab content
        stats_frame = ttk.Frame(self.app.stats_tab, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            stats_frame, 
            text="📊 Task Statistics", 
            font=("Helvetica", 16, "bold")
        )
        header.pack(pady=(0, 20))
        
        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.BOTH, expand=True)
        
        # Total tasks
        total_frame = ttk.LabelFrame(stats_grid, text="Total Tasks")
        total_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.total_var = tk.StringVar(value="0")
        total_label = ttk.Label(
            total_frame, 
            textvariable=self.total_var,
            font=("Helvetica", 24, "bold"),
            foreground="#00BFFF"
        )
        total_label.pack(pady=10)
        
        # Completed tasks
        completed_frame = ttk.LabelFrame(stats_grid, text="Completed")
        completed_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.completed_var = tk.StringVar(value="0")
        completed_label = ttk.Label(
            completed_frame, 
            textvariable=self.completed_var,
            font=("Helvetica", 24, "bold"),
            foreground="#32CD32"
        )
        completed_label.pack(pady=10)
        
        # Pending tasks
        pending_frame = ttk.LabelFrame(stats_grid, text="Pending")
        pending_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.pending_var = tk.StringVar(value="0")
        pending_label = ttk.Label(
            pending_frame, 
            textvariable=self.pending_var,
            font=("Helvetica", 24, "bold"),
            foreground="#FF8C00"
        )
        pending_label.pack(pady=10)
        
        # Make columns expandable
        for i in range(3):
            stats_grid.columnconfigure(i, weight=1)
        
        # Category distribution
        category_frame = ttk.LabelFrame(stats_grid, text="Tasks by Category")
        category_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        self.category_stats = ttk.Frame(category_frame)
        self.category_stats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Priority distribution pie chart
        priority_frame = ttk.LabelFrame(stats_grid, text="Tasks by Priority")
        priority_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        self.priority_chart = ttk.Frame(priority_frame)
        self.priority_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update statistics when the tab is first created
        self.update_statistics()

    def update_statistics(self):
        # Update task counts
        total = len(self.app.tasks)
        completed = sum(1 for task in self.app.tasks if task.get("completed", False))
        pending = total - completed
        
        # Check if the StringVars exist before setting them (can happen during init)
        if hasattr(self, 'total_var'):
            self.total_var.set(str(total))
        if hasattr(self, 'completed_var'):
            self.completed_var.set(str(completed))
        if hasattr(self, 'pending_var'):
            self.pending_var.set(str(pending))
        
        # Update category statistics
        # Check if the category_stats frame exists
        if hasattr(self, 'category_stats'):
            for widget in self.category_stats.winfo_children():
                widget.destroy()
            
            # Count tasks by category
            category_counts = {}
            for task in self.app.tasks:
                category = task.get("category", "None")
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Display category counts
            for i, (category, count) in enumerate(category_counts.items()):
                cat_label = ttk.Label(self.category_stats, text=f"{category}: {count} tasks")
                cat_label.grid(row=i, column=0, sticky="w", pady=2)
        
        # Update priority pie chart
        # Check if the priority_chart frame exists
        if hasattr(self, 'priority_chart'):
            self.update_priority_chart()

    def update_priority_chart(self):
        # Clear existing chart
        for widget in self.priority_chart.winfo_children():
            widget.destroy()
        
        # Count tasks by priority
        priority_counts = {"Low": 0, "Medium": 0, "High": 0, "Urgent": 0}
        for task in self.app.tasks:
            priority = task.get("priority", "Medium")
            if priority in priority_counts: # Ensure priority is valid
                 priority_counts[priority] += 1
        
        # Calculate the total number of tasks with valid priorities
        total_priorities = sum(priority_counts.values())
        
        # Only draw the chart if there are tasks to plot
        if total_priorities > 0:
            # Create pie chart
            # Use a non-interactive backend suitable for Tkinter embedding
            fig, ax = plt.subplots(figsize=(5, 4), facecolor=self.app.root.cget('bg')) # Match background
            ax.set_facecolor(self.app.root.cget('bg')) # Match background
            
            # Filter out priorities with zero count to avoid plotting issues
            plot_labels = [k for k, v in priority_counts.items() if v > 0]
            plot_values = [v for v in priority_counts.values() if v > 0]
            
            # Define colors (optional, but makes it look consistent)
            colors = ['#3CB371', '#1E90FF', '#FF8C00', '#DC143C'] # Low, Medium, High, Urgent
            plot_colors = [colors[self.app.priority_levels.index(p)] for p in plot_labels]

            wedges, texts, autotexts = ax.pie(
                plot_values, 
                labels=plot_labels, 
                colors=plot_colors,
                autopct='%1.1f%%', 
                startangle=90,
                pctdistance=0.85 # Move percentage text inside wedges slightly
            )
            
            # Style the percentage text
            for autotext in autotexts:
                autotext.set_color('white') # Set percentage text color
                autotext.set_fontsize(10)

            # Style the labels
            for text in texts:
                 text.set_color('gray') # Set label text color
                 text.set_fontsize(10)

            ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
            
            # Embed the plot in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.priority_chart)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Display a message if there's no data
            no_data_label = ttk.Label(self.priority_chart, text="No priority data to display.", anchor="center")
            no_data_label.pack(fill=tk.BOTH, expand=True)

