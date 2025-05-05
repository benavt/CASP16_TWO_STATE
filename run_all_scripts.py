#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
import time

def run_python_script(script_path):
    """Run a Python script and return its execution status."""
    print(f"\n{'='*80}")
    print(f"Running: {script_path}")
    print(f"{'='*80}")
    
    try:
        # Store the original working directory
        original_cwd = os.getcwd()
        
        # Change to the script's directory
        script_dir = script_path.parent
        os.chdir(script_dir)
        
        # Run the script and capture output
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, 
                              text=True)
        
        # Restore the original working directory
        os.chdir(original_cwd)
        
        # Print output
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        # Print errors if any
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Return status
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running {script_path}: {str(e)}")
        # Ensure we restore the original directory even if there's an error
        try:
            os.chdir(original_cwd)
        except:
            pass
        return False

def main():
    # Get the current directory
    current_dir = Path.cwd()
    
    # Find all Python files recursively
    python_files = list(current_dir.rglob("*.py"))
    
    # Exclude the current script from execution
    python_files = [f for f in python_files if f.name != "run_all_scripts.py"]
    
    if not python_files:
        print("No Python files found in the current directory and subdirectories.")
        return
    
    print(f"Found {len(python_files)} Python files to execute.")
    
    # Track execution results
    successful = 0
    failed = 0
    
    # Run each script
    for script in python_files:
        start_time = time.time()
        success = run_python_script(script)
        end_time = time.time()
        
        if success:
            successful += 1
            status = "SUCCESS"
        else:
            failed += 1
            status = "FAILED"
            
        print(f"\nExecution time: {end_time - start_time:.2f} seconds")
        print(f"Status: {status}")
    
    # Print summary
    print("\n" + "="*80)
    print("Execution Summary:")
    print(f"Total scripts: {len(python_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print("="*80)

if __name__ == "__main__":
    main() 