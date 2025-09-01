import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import pandas as pd

# Import classes from our modules
from processor import DataProcessor
from analyzer import DataAnalyzer
from reporter import SalesReporter

class SalesApp:
    """
    Main application class that manages the GUI and orchestrates the workflow.
    """
    def __init__(self, root):
        """
        Initializes the application with a Tkinter root window.

        Args:
            root (tk.Tk): The main Tkinter window.
        """
        self.root = root
        self.root.title("Sales Report Generator")
        self.root.geometry("1000x1000")  # Increased height to accommodate charts

        self.filepath = None
        self.report_image = None
        self.report_path = None  # Store report path for PDF saving

        self._create_widgets()

    def _create_widgets(self):
        """Creates and organizes the GUI widgets."""
        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.btn_select = tk.Button(control_frame, text="1. Select CSV File", command=self._select_file)
        self.btn_select.pack(side=tk.LEFT, padx=10)

        self.btn_generate = tk.Button(control_frame, text="2. Generate Report", command=self._generate_report, state=tk.DISABLED)
        self.btn_generate.pack(side=tk.LEFT, padx=10)

        self.btn_save_pdf = tk.Button(control_frame, text="3. Save as PDF", command=self._save_as_pdf, state=tk.DISABLED)
        self.btn_save_pdf.pack(side=tk.LEFT, padx=10)

        # Status bar label
        self.status_label = tk.Label(self.root, text="Waiting for file selection...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
        
        # PanedWindow to split the interface into two columns
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Left frame for CSV preview
        preview_frame = tk.Frame(paned_window)
        paned_window.add(preview_frame)

        preview_label = tk.Label(preview_frame, text="CSV File Preview (First 100 Lines):")
        preview_label.pack()

        # Text widget with scrollbars for preview
        self.preview_text = tk.Text(preview_frame, wrap=tk.NONE)
        self.preview_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.scrollbar_y = tk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = tk.Scrollbar(preview_frame, command=self.preview_text.xview, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_text.config(xscrollcommand=self.scrollbar_x.set)

        # Right frame for report image
        report_frame = tk.Frame(paned_window)
        paned_window.add(report_frame)

        self.report_canvas = tk.Label(report_frame)
        self.report_canvas.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        
        # Set initial sash position to 30% of window width
        initial_width = int(self.root.winfo_reqwidth() * 0.3)
        paned_window.sash_place(0, initial_width, 1)

    def _select_file(self):
        """Opens a file dialog for the user to select a CSV file and displays its preview."""
        self.filepath = filedialog.askopenfilename(
            title="Select a Sales CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )
        if self.filepath:
            # Validate file extension
            if not self.filepath.lower().endswith('.csv'):
                self.status_label.config(text="Invalid file format. Please select a CSV file.")
                self.btn_generate.config(state=tk.DISABLED)
                self.btn_save_pdf.config(state=tk.DISABLED)
                self.preview_text.delete('1.0', tk.END)
                return
            self.status_label.config(text=f"Selected file: {os.path.basename(self.filepath)}")
            self.btn_generate.config(state=tk.NORMAL)
            self.btn_save_pdf.config(state=tk.DISABLED)  # Disable PDF button until report is generated
            self._display_preview()
        else:
            self.status_label.config(text="File selection canceled.")
            self.btn_generate.config(state=tk.DISABLED)
            self.btn_save_pdf.config(state=tk.DISABLED)
            self.preview_text.delete('1.0', tk.END)

    def _display_preview(self):
        """Reads and displays the first 100 lines of the CSV file in the text widget."""
        try:
            self.preview_text.delete('1.0', tk.END)  # Clear previous content
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Join up to 101 lines to include 100 data rows plus header
            preview_content = "".join(lines[:101])
            self.preview_text.insert('1.0', preview_content)
        except Exception as e:
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"Error loading preview: {e}")

    def _generate_report(self):
        """
        Orchestrates the workflow: process -> analyze -> report.
        Updates the status and displays the final report.
        """
        if not self.filepath:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return

        self.status_label.config(text="Processing data...")
        self.root.update_idletasks()
        
        try:
            # 1. Data processing
            processor = DataProcessor(self.filepath)
            processed_df = processor.process_data()
            
            if processed_df is None:
                raise ValueError("Error processing data. Check the input file.")

            # 2. Data analysis
            self.status_label.config(text="Analyzing data...")
            self.root.update_idletasks()
            analyzer = DataAnalyzer(processed_df)
            analysis_results = {
                'summary_stats': analyzer.get_summary_stats(),
                'sales_by_product': analyzer.get_sales_by_product(),
                'sales_by_period': analyzer.get_sales_by_period(),
                'sales_by_category': analyzer.get_sales_by_category()
            }

            # 3. Generate visual report
            self.status_label.config(text="Generating report...")
            self.root.update_idletasks()
            reporter = SalesReporter(analysis_results)
            reporter.generate_charts()
            self.report_path = reporter.compile_report()

            # 4. Display report
            self._display_report(self.report_path)
            self.btn_save_pdf.config(state=tk.NORMAL)  # Enable PDF save button
            self.status_label.config(text="Report generated successfully!")
        
        except Exception as e:
            # Capture detailed error message and display in a dialog
            error_message = f"Failed to generate report.\n\nError Details:\n{e}"
            messagebox.showerror("Report Generation Error", error_message)
            self.status_label.config(text="Failed to generate report.")
            self.btn_save_pdf.config(state=tk.DISABLED)

    def _display_report(self, report_path):
        """Loads and displays the report image in the GUI canvas."""
        try:
            image = Image.open(report_path)
            # Resize image to fit the right pane while maintaining aspect ratio
            right_pane_width = int(self.root.winfo_width() * 0.7 - 60)  # Approximate right pane width (70%)
            image.thumbnail((right_pane_width, self.root.winfo_height() - 150), Image.Resampling.LANCZOS)
            self.report_image = ImageTk.PhotoImage(image)
            self.report_canvas.config(image=self.report_image)
            self.report_canvas.image = self.report_image
        except Exception as e:
            messagebox.showerror("Display Error", f"Unable to display report: {e}")
            self.btn_save_pdf.config(state=tk.DISABLED)

    def _save_as_pdf(self):
        """Saves the generated report image as a PDF file."""
        if not self.report_path or not os.path.exists(self.report_path):
            messagebox.showerror("Error", "No report available to save as PDF.")
            return

        # Open file dialog to choose save location
        pdf_path = filedialog.asksaveasfilename(
            title="Save Report as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if not pdf_path:
            self.status_label.config(text="PDF save canceled.")
            return

        try:
            # Convert the report image to PDF
            image = Image.open(self.report_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')  # Ensure compatibility with PDF
            image.save(pdf_path, "PDF", resolution=100.0)
            self.status_label.config(text=f"Report saved as PDF: {os.path.basename(pdf_path)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save PDF: {e}")
            self.status_label.config(text="Failed to save PDF.")

# Application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()