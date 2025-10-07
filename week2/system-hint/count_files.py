#!/usr/bin/env python3
"""
File counter script - counts files in the current directory
"""

import os
import sys
from pathlib import Path

def count_files_in_directory(directory="."):
    """Count files in the specified directory"""
    try:
        # Get all items in directory
        items = os.listdir(directory)
        
        # Count only files (not directories)
        file_count = 0
        files_list = []
        
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_count += 1
                files_list.append(item)
        
        return file_count, files_list
        
    except Exception as e:
        print(f"Error reading directory: {e}")
        return 0, []

def main():
    """Main function"""
    current_dir = os.getcwd()
    print(f"Counting files in directory: {current_dir}")
    print("-" * 50)
    
    file_count, files_list = count_files_in_directory()
    
    print(f"Total files found: {file_count}")
    print("\nFiles:")
    
    if files_list:
        for i, file in enumerate(files_list, 1):
            print(f"{i:2d}. {file}")
    else:
        print("No files found in current directory.")
    
    return file_count

if __name__ == "__main__":
    main()