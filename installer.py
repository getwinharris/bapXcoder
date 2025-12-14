#!/usr/bin/env python3
"""
bapXcoder Universal Installer
GUI-based installer with visual feedback during installation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import sys
import os
import time
from pathlib import Path
import json
import platform


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
            "Downloading AI model (5-6GB)",
            "Configuring application",
            "Creating shortcuts",
            "Finalizing installation"
        ]
        
        self.setup_ui()
        
    def setup_window(self):
        self.root.title("bapXcoder Installation Wizard")
        self.root.geometry("650x550")
        
        # Set window icon - would use your logo in production
        try:
            # In a real implementation, you'd load your logo here
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
        main_frame.columnconfigure(0, weight=1)
        
        # Header with logo representation
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="⚡ bapXcoder", font=("Arial", 18, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="AI-Powered IDE with Project Memory", font=("Arial", 10))
        subtitle_label.pack()
        
        # Description
        desc_label = ttk.Label(main_frame, text="Welcome to the bapXcoder installation wizard", font=("Arial", 10))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
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
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=450)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, wraplength=550)
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Console output
        console_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="10")
        console_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console_output = scrolledtext.ScrolledText(console_frame, height=10, state='disabled', font=("Consolas", 9))
        self.console_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        self.install_btn = ttk.Button(button_frame, text="Install bapXcoder", command=self.start_installation)
        self.install_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_installation)
        self.cancel_btn.grid(row=0, column=1)
        
        # Configure grid weights
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.install_path.get(), title="Select Installation Directory")
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
        self.console_output.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.console_output.see(tk.END)
        self.console_output.config(state='disabled')
    
    def update_status(self, step_index, message):
        self.status_var.set(message)
        progress = (step_index / len(self.installation_steps)) * 100
        self.progress_var.set(progress)
        self.update_console(f"Step {step_index+1}/{len(self.installation_steps)}: {message}")
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
            success = self.setup_python_environment()
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
            self.update_status(4, "Downloading AI model (~5-6GB)...")
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
            self.update_status(6, "Creating desktop shortcuts...")
            success = self.create_shortcuts()
            if not success:
                self.restore_buttons()
                return
            
            # Step 8: Finalize installation
            self.update_status(7, "Finalizing installation...")
            self.finalize_installation()
            
            # Complete
            self.progress_var.set(100)
            self.status_var.set("Installation Complete!")
            self.update_console("✓ bapXcoder installation completed successfully!")
            messagebox.showinfo("Success", f"bapXcoder has been installed to:\n{self.install_path.get()}\n\nClick OK to launch the application.")
            
            # Ask if user wants to start the application
            if messagebox.askyesno("Launch", "Do you want to start bapXcoder now?", icon='question'):
                self.launch_application()
            
            self.root.destroy()
            
        except Exception as e:
            self.update_console(f"ERROR: {str(e)}")
            messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")
            self.restore_buttons()
    
    def verify_requirements(self):
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            self.update_console("ERROR: Python 3.8 or higher is required")
            return False
        
        # Check if git is available
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.update_console("ERROR: Git is required but not found in PATH")
                return False
        except FileNotFoundError:
            self.update_console("ERROR: Git is required but not found in PATH")
            return False
        
        self.update_console(f"✓ Verified Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} requirement")
        self.update_console("✓ Verified Git installation")
        return True
    
    def clone_repository(self):
        try:
            install_dir = Path(self.install_path.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Change to the installation directory
            os.chdir(install_dir)
            
            self.update_console(f"Cloning repository to: {install_dir}")
            
            # Run git clone command
            result = subprocess.run([
                'git', 'clone', 'https://github.com/getwinharris/bapXcoder.git', '.'
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                self.update_console(f"ERROR: Failed to clone repository: {result.stderr}")
                return False
            
            self.update_console("✓ Repository cloned successfully")
            return True
        except subprocess.TimeoutExpired:
            self.update_console("ERROR: Repository cloning timed out")
            return False
        except Exception as e:
            self.update_console(f"ERROR: Failed to clone repository: {str(e)}")
            return False
    
    def setup_python_environment(self):
        try:
            import sys
            self.update_console(f"Using Python: {sys.executable}")
            
            # Create virtual environment
            result = subprocess.run([
                sys.executable, '-m', 'venv', 'venv'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                self.update_console(f"ERROR: Failed to create virtual environment: {result.stderr}")
                return False
            
            self.update_console("✓ Python virtual environment created")
            return True
        except subprocess.TimeoutExpired:
            self.update_console("ERROR: Virtual environment setup timed out")
            return False
        except Exception as e:
            self.update_console(f"ERROR: Failed to set up Python environment: {str(e)}")
            return False
    
    def install_dependencies(self):
        try:
            # Activate virtual environment and install dependencies
            if platform.system() == "Windows":
                pip_path = str(Path(self.install_path.get()) / "venv" / "Scripts" / "pip.exe")
            else:
                pip_path = str(Path(self.install_path.get()) / "venv" / "bin" / "pip")
            
            self.update_console("Installing required packages...")
            
            result = subprocess.run([
                pip_path, 'install', '--upgrade', 'pip'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.update_console(f"ERROR: Failed to upgrade pip: {result.stderr}")
                return False
            
            result = subprocess.run([
                pip_path, 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout for dependencies
            
            if result.returncode != 0:
                self.update_console(f"ERROR: Failed to install dependencies: {result.stderr}")
                return False
            
            self.update_console("✓ Dependencies installed successfully")
            return True
        except subprocess.TimeoutExpired:
            self.update_console("ERROR: Dependency installation timed out")
            return False
        except Exception as e:
            self.update_console(f"ERROR: Failed to install dependencies: {str(e)}")
            return False
    
    def download_model(self):
        try:
            self.update_console("Starting AI model download (~5-6GB)...")
            
            # Run the download script
            result = subprocess.run([
                sys.executable, 'download_model.py'
            ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout for model download
            
            if result.returncode != 0:
                self.update_console(f"ERROR: Failed to download model: {result.stderr}")
                return False
            
            self.update_console("✓ AI model downloaded successfully")
            return True
        except subprocess.TimeoutExpired:
            self.update_console("ERROR: Model download timed out (may take 30+ minutes on slower connections)")
            return False
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
            config_data = {
                "install_date": time.time(),
                "version": "1.0.0",
                "install_path": str(self.install_path.get()),
                "model_downloaded": True
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.update_console("✓ Application configured")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to configure application: {str(e)}")
            return False
    
    def create_shortcuts(self):
        try:
            install_path = Path(self.install_path.get())
            
            # Create a start script
            start_script = install_path / "start_bapXcoder.py"
            start_script_content = '''#!/usr/bin/env python3
"""
Start script for bapXcoder
Launches the application after installation
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("Starting bapXcoder...")
    print("Opening in browser at http://localhost:7860")
    
    # Activate virtual environment if it exists
    venv_dir = Path(__file__).parent / "venv"
    if venv_dir.exists():
        if os.name == "nt":  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:  # Unix-like systems
            python_exe = venv_dir / "bin" / "python"
        
        if python_exe.exists():
            subprocess.run([str(python_exe), "qwen3VL_local_cli.py"])
        else:
            print("Virtual environment Python not found, using system Python")
            subprocess.run([sys.executable, "qwen3VL_local_cli.py"])
    else:
        print("Virtual environment not found, using system Python")
        subprocess.run([sys.executable, "qwen3VL_local_cli.py"])

if __name__ == "__main__":
    main()
'''
            start_script.write_text(start_script_content)
            
            # Make it executable on Unix-like systems
            if os.name != "nt":
                start_script.chmod(0o755)
            
            self.update_console("✓ Start script created")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to create shortcuts: {str(e)}")
            return False
    
    def finalize_installation(self):
        try:
            install_dir = Path(self.install_path.get())
            
            # Create completion marker
            completion_file = install_dir / ".installed"
            completion_file.write_text(f"Installed at {time.time()}")
            
            self.update_console("✓ Installation finalized")
            return True
        except Exception as e:
            self.update_console(f"ERROR: Failed to finalize installation: {str(e)}")
            return False
    
    def launch_application(self):
        try:
            # Find and run start script
            start_script = Path(self.install_path.get()) / "start_bapXcoder.py"
            if start_script.exists():
                # Use the virtual environment Python if available
                venv_dir = Path(self.install_path.get()) / "venv"
                if venv_dir.exists():
                    if platform.system() == "Windows":
                        python_exe = venv_dir / "Scripts" / "python.exe"
                    else:
                        python_exe = venv_dir / "bin" / "python"
                    
                    if python_exe.exists():
                        subprocess.Popen([str(python_exe), str(start_script)])
                    else:
                        subprocess.Popen([sys.executable, str(start_script)])
                else:
                    subprocess.Popen([sys.executable, str(start_script)])
            else:
                messagebox.showwarning("Launch Warning", "Start script not found. Installation may be incomplete.")
        except Exception as e:
            self.update_console(f"ERROR: Failed to launch application: {str(e)}")
            messagebox.showerror("Launch Error", f"Failed to launch bapXcoder: {str(e)}")
    
    def restore_buttons(self):
        self.install_btn.config(state='enabled')


def main():
    app = InstallationWizard()
    app.root.mainloop()


if __name__ == "__main__":
    main()