#!/usr/bin/env python3
"""
GitHub Wiki Manual Setup Helper
Prints wiki content that can be copied to GitHub wiki pages
"""

import os
from pathlib import Path

def print_wiki_setup():
    """Print setup instructions and wiki content for manual copying"""
    
    print("🚀 GitHub Wiki Manual Setup")
    print("=" * 60)
    print()
    print("The GitHub wiki is empty because it needs to be manually initialized.")
    print("Follow these steps to populate it with our comprehensive documentation:")
    print()
    
    # Wiki files mapping
    wiki_files = {
        "Home": "wiki/Home.md",
        "Quick-Start": "wiki/Quick-Start.md", 
        "Installation-Guide": "wiki/Installation-Guide.md",
        "Configuration": "wiki/Configuration.md",
        "API-Reference": "wiki/API-Reference.md",
        "System-Architecture": "wiki/System-Architecture.md",
        "n8n-Integration": "wiki/n8n-Integration.md"
    }
    
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    print("1. Go to: https://github.com/navidrast/cloudviz/wiki")
    print("2. Click 'Create the first page'")
    print("3. Follow the instructions below for each page")
    print()
    
    for i, (page_name, file_path) in enumerate(wiki_files.items(), 1):
        print(f"📄 PAGE {i}: {page_name}")
        print("-" * 40)
        print(f"• Page Title: {page_name}")
        print(f"• Source File: {file_path}")
        
        # Try to read the file content
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    chars = len(content)
                    print(f"• Content: {lines} lines, {chars} characters")
                    print(f"• Preview: {content[:100]}...")
            except Exception as e:
                print(f"• Error reading file: {e}")
        else:
            print(f"• File not found: {file_path}")
        
        print()
    
    print("🔄 QUICK COPY-PASTE METHOD:")
    print()
    print("For each page above:")
    print("1. Create new wiki page with the exact title")
    print("2. Copy the entire content from the source file")
    print("3. Paste it into the wiki page editor")
    print("4. Save the page")
    print()
    
    print("📁 ALL CONTENT READY IN:")
    for file_path in wiki_files.values():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path} (missing)")
    
    print()
    print("🎉 RESULT:")
    print("Once all pages are created, your wiki will be live at:")
    print("https://github.com/navidrast/cloudviz/wiki")
    print()
    print("With complete documentation covering:")
    print("• Installation & Setup")
    print("• API Reference (44 endpoints)")
    print("• System Architecture") 
    print("• n8n Integration & Automation")
    print("• Configuration & Security")
    print()

def print_file_content(filename):
    """Print the content of a specific wiki file"""
    
    file_path = f"wiki/{filename}.md"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📄 Content for {filename} page:")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
    
    print()
    print("=" * 60)
    print(f"📋 Copy the above content to create the '{filename}' wiki page")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Print specific file content
        filename = sys.argv[1]
        print_file_content(filename)
    else:
        # Print setup instructions
        print_wiki_setup()
