#!/usr/bin/env python3
"""
Sync script to copy all Python files from MockPricingAgent repo to webapp
"""

import shutil
import os
from pathlib import Path
import sys

# Configuration
SOURCE_DIR = r"C:\Repos\MockPricingAgent"
DEST_DIR = r"src\multi_agent"

def sync_files():
    """Copy all .py files from source to destination"""
    
    # Get the script's directory to make paths relative
    script_dir = Path(__file__).parent
    webapp_root = script_dir.parent
    dest_path = webapp_root / DEST_DIR
    source_path = Path(SOURCE_DIR)
    
    # Check if source directory exists
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_path}")
        print(f"   Please ensure {SOURCE_DIR} exists")
        return False
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .py files in source directory
    py_files = list(source_path.glob("*.py"))
    
    if not py_files:
        print(f"❌ No .py files found in {source_path}")
        return False
    
    print(f"📁 Syncing from: {source_path}")
    print(f"📁 Syncing to:   {dest_path}")
    print(f"📄 Found {len(py_files)} Python files")
    print()
    
    # Copy each .py file
    copied_files = []
    for py_file in py_files:
        try:
            dest_file = dest_path / py_file.name
            shutil.copy2(py_file, dest_file)
            copied_files.append(py_file.name)
            print(f"✅ Copied: {py_file.name}")
        except Exception as e:
            print(f"❌ Failed to copy {py_file.name}: {e}")
            return False
    
    # Also copy requirements.txt if it exists
    requirements_file = source_path / "requirements.txt"
    if requirements_file.exists():
        try:
            dest_req = dest_path / "requirements.txt"
            shutil.copy2(requirements_file, dest_req)
            print(f"✅ Copied: requirements.txt")
        except Exception as e:
            print(f"⚠️  Failed to copy requirements.txt: {e}")
    
    # Create .gitignore to ignore this directory
    gitignore_path = dest_path / ".gitignore"
    try:
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore all files in this directory (synced from external repo)\n")
            f.write("*\n")
            f.write("!.gitignore\n")
        print(f"✅ Created: .gitignore")
    except Exception as e:
        print(f"⚠️  Failed to create .gitignore: {e}")
    
    print()
    print(f"✅ Successfully synced {len(copied_files)} files!")
    print(f"   Files: {', '.join(copied_files)}")
    
    return True

def main():
    """Main function"""
    print("🔄 MockPricingAgent Sync Script")
    print("=" * 40)
    
    if sync_files():
        print()
        print("🎉 Sync completed successfully!")
        print("   You can now run the webapp with the updated multi-agent code.")
    else:
        print()
        print("💥 Sync failed!")
        print("   Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
