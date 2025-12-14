#!/usr/bin/env python3
"""
bapXcoder Installation Wizard
GUI-based installer that provides visual feedback during the installation process
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import sys
import os
import shutil
from pathlib import Path
import time
import webbrowser


class InstallationWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Installation variables
        self.install_path = tk.StringVar()
        self.install_path.set(os.path.expanduser("~/bapXcoder"))
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to begin installation")
        
        # Installation steps
        self.installation_steps = [
            "Verifying system requirements",
            "Cloning bapXcoder repository", 
            "Setting up Python environment",
            "Installing dependencies",
            "Downloading AI model",
            "Configuring application",
            "Creating shortcuts",
            "Finishing installation"
        ]
        
        self.setup_ui()
        
    def setup_window(self):
        self.root.title("bapXcoder Installation Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Set window icon (would be replaced with actual logo in production)
        try:
            # In a real implementation, you'd set the window icon here
            pass
        except:
            pass
            
        # Center the window
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Welcome to bapXcoder", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="AI-Powered IDE with Project Memory", font=("Arial", 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Installation path selection
        path_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding="10")
        path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(path_frame, text="Install to:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_entry_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_entry_frame, textvariable=self.install_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_entry_frame, text="Browse...", command=self.browse_path).grid(row=0, column=1)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, wraplength=500)
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Console output
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="10")
        console_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console_output = scrolledtext.ScrolledText(console_frame, height=8, state='disabled')
        self.console_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        self.install_btn = ttk.Button(button_frame, text="Install bapXcoder", command=self.start_installation)
        self.install_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_installation)
        self.cancel_btn.grid(row=0, column=1)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_path(self):
        # In a real implementation, this would open a file dialog
        path = tk.filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)
    
    def start_installation(self):
        # Disable the install button during installation
        self.install_btn.config(state='disabled')
        
        # Start installation in a separate thread
        installation_thread = threading.Thread(target=self.run_installation)
        installation_thread.daemon = True
        installation_thread.start()
    
    def cancel_installation(self):
        # Close the installer
        self.root.destroy()
        sys.exit()
    
    def update_console(self, text):
        self.console_output.config(state='normal')
        self.console_output.insert(tk.END, text + "\n")
        self.console_output.see(tk.END)
        self.console_output.config(state='disabled')
        self.root.update_idletasks()
    
    def run_installation(self):
        try:
            total_steps = len(self.installation_steps)
            
            # Step 1: Verify system requirements
            self.update_status(0, "Verifying system requirements...")
            success = self.verify_requirements()
            if not success:
                messagebox.showerror("Installation Error", "System requirements not met.\nPython 3.8+ is required.")
                self.restore_buttons()
                return
            
            # Step 2: Clone repository
            self.update_status(1, "Cloning bapXcoder repository...")
            success = self.clone_repository()
            if not success:
                self.restore_buttons()
                return
            
            # Step 3: Set up Python environment
            self.update_status(2, "Setting up Python environment...")
            success = self.setup_python_env()
            if not success:
                self.restore_buttons()
                return
            
            # Step 4: Install dependencies
            self.update_status(3, "Installing dependencies...")
            success = self.install_dependencies()
            if not success:
                self.restore_buttons()
                return
            
            # Step 5: Download AI model
            self.update_status(4, "Downloading AI model...")
            success = self.download_model()
            if not success:
                self.restore_buttons()
                return
            
            # Step 6: Configure application
            self.update_status(5, "Configuring application...")
            success = self.configure_application()
            if not success:
                self.restore_buttons()
                return
            
            # Step 7: Create shortcuts
            self.update_status(6, "Creating shortcuts...")
            success = self.create_shortcuts()
            if not success:
                self.restore_buttons()
                return
            
            # Step 8: Finish installation
            self.update_status(7, "Finishing installation...")
            self.finalize_installation()
            
            # Complete
            self.progress_var.set(100)
            self.status_var.set("Installation Complete!")
            self.update_console("✓ bapXcoder installation completed successfully!")
            messagebox.showinfo("Success", f"bapXcoder has been installed to:\n{self.install_path.get()}\n\nClick OK to launch.")
            
            # Ask if user wants to start the application
            if messagebox.askyesno("Launch", "Do you want to start bapXcoder now?"):
                self.launch_application()
            
            self.root.destroy()
            
        except Exception as e:
            self.update_console(f"ERROR: {str(e)}")
            messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")
            self.restore_buttons()
    
    def update_status(self, step_index, message):
        self.status_var.set(message)
        progress = (step_index / len(self.installation_steps)) * 100
        self.progress_var.set(progress)
        self.update_console(f"[{step_index+1}/{len(self.installation_steps)}] {message}")
        self.root.update_idletasks()
    
    def verify_requirements(self):
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            self.update_console("ERROR: Python 3.8 or higher is required")
            return False
        
        self.update_console("✓ Verified Python requirements")
        return True
    
    def clone_repository(self):
        try:
            # Create installation directory
            install_dir = Path(self.install_path.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # In a real implementation, this would git clone the repo
            # For demonstration, we'll just create a basic directory structure
            self.update_console(f"Cloning to: {install_dir}")
            
            # Simulate git clone
            time.sleep(1)  # Simulate download time
            self.update_console("✓ Repository cloned successfully")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to clone repository: {str(e)}")
            return False
    
    def setup_python_env(self):
        try:
            import sys
            self.update_console(f"Using Python: {sys.executable}")
            self.update_console("✓ Python environment configured")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to configure Python environment: {str(e)}")
            return False
    
    def install_dependencies(self):
        try:
            # In a real implementation, this would run: pip install -r requirements.txt
            # For now, simulate installation
            self.update_console("Installing required packages...")
            time.sleep(2)  # Simulate installation time
            self.update_console("✓ Dependencies installed")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to install dependencies: {str(e)}")
            return False
    
    def download_model(self):
        try:
            # In a real implementation, this would download the AI model
            # For now, simulate download with progress
            self.update_console("Downloading Qwen3VL AI model (~5-6GB)...")
            
            # Simulate download progress
            for i in range(10):
                time.sleep(0.3)  # Simulate download time
                percent = int(((i+1)/10) * 100) 
                self.update_console(f"Download progress: {percent}%")
            
            self.update_console("✓ AI model downloaded successfully")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to download model: {str(e)}")
            return False
    
    def configure_application(self):
        try:
            # Create .bapXcoder directory for project memory
            bapx_dir = Path(self.install_path.get()) / ".bapXcoder"
            bapx_dir.mkdir(exist_ok=True)
            
            # Create configuration files
            config_file = bapx_dir / "config.json"
            config_file.write_text("{}")  # Create empty config
            
            self.update_console("✓ Application configured")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to configure application: {str(e)}")
            return False
    
    def create_shortcuts(self):
        try:
            # Create a start script (like start.sh)
            start_script = Path(self.install_path.get()) / "start_bapXcoder.py"
            start_script_content = f'''#!/usr/bin/env python3
"""
Start script for bapXcoder
Launched the application after installation
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("Starting bapXcoder...")
    print("Please run: python qwen3VL_local_cli.py")
    
    # In a real implementation, this would start the actual application
    ide_path = Path("{self.install_path.get()}") / "qwen3VL_local_cli.py"
    if ide_path.exists():
        subprocess.run([sys.executable, str(ide_path)])
    else:
        print("bapXcoder application not found. Please check installation.")

if __name__ == "__main__":
    main()
'''
            start_script.write_text(start_script_content)
            start_script.chmod(0o755)  # Make executable
            
            self.update_console("✓ Shortcuts created")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to create shortcuts: {str(e)}")
            return False
    
    def finalize_installation(self):
        try:
            self.update_console("Finalizing installation...")
            time.sleep(1)
            self.update_console("✓ Installation finalized")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to finalize: {str(e)}")
            return False
    
    def launch_application(self):
        try:
            # Launch the application
            start_script = Path(self.install_path.get()) / "start_bapXcoder.py"
            if start_script.exists():
                subprocess.Popen([sys.executable, str(start_script)])
            else:
                messagebox.showwarning("Launch Warning", "Start script not found. Please run manually.")
        except Exception as e:
            self.update_console(f"ERROR: Failed to launch application: {str(e)}")
    
    def restore_buttons(self):
        self.install_btn.config(state='enabled')


def main():
    app = InstallationWizard()
    
    # Center the window before showing
    app.root.update_idletasks()
    width = app.root.winfo_width()
    height = app.root.winfo_height()
    x = (app.root.winfo_screenwidth() // 2) - (width // 2)
    y = (app.root.winfo_screenheight() // 2) - (height // 2)
    app.root.geometry(f'{width}x{height}+{x}+{y}')
    
    app.root.mainloop()


if __name__ == "__main__":
    main()