#!/usr/bin/env python3
"""
GitHub Wiki Deployment Script for CloudViz
Automatically deploys wiki content to GitHub wiki repository
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {cmd}: {e}")
        return False

def deploy_wiki():
    """Deploy wiki content to GitHub wiki repository"""
    
    # Configuration
    REPO_URL = "https://github.com/navidrast/cloudviz.wiki.git"
    WIKI_SOURCE = "wiki"
    WIKI_TEMP = "temp_wiki_deploy"
    
    print("🚀 CloudViz Wiki Deployment Script")
    print("=" * 50)
    
    # Check if wiki source exists
    if not os.path.exists(WIKI_SOURCE):
        print(f"❌ Error: Wiki source directory '{WIKI_SOURCE}' not found!")
        print("Make sure you're running this from the CloudViz repository root.")
        return False
    
    # List wiki files
    wiki_files = list(Path(WIKI_SOURCE).glob("*.md"))
    print(f"📚 Found {len(wiki_files)} wiki files to deploy:")
    for file in wiki_files:
        print(f"   - {file.name}")
    
    print("\n🔄 Step 1: Cloning wiki repository...")
    
    # Clean up any existing temp directory
    if os.path.exists(WIKI_TEMP):
        shutil.rmtree(WIKI_TEMP)
    
    # Clone the wiki repository
    if not run_command(f"git clone {REPO_URL} {WIKI_TEMP}"):
        print("❌ Failed to clone wiki repository.")
        print("📝 Note: If the wiki doesn't exist yet, you need to:")
        print("   1. Go to https://github.com/navidrast/cloudviz/wiki")
        print("   2. Click 'Create the first page'")
        print("   3. Create a page titled 'Home'")
        print("   4. Then run this script again")
        return False
    
    print("✅ Wiki repository cloned successfully!")
    
    print("\n📁 Step 2: Copying wiki files...")
    
    # Copy wiki files with proper naming
    file_mapping = {
        "Home.md": "Home.md",
        "Quick-Start.md": "Quick-Start.md",
        "Installation-Guide.md": "Installation-Guide.md",
        "Configuration.md": "Configuration.md",
        "API-Reference.md": "API-Reference.md", 
        "System-Architecture.md": "System-Architecture.md",
        "n8n-Integration.md": "n8n-Integration.md"
    }
    
    copied_files = 0
    for source_file, dest_file in file_mapping.items():
        source_path = os.path.join(WIKI_SOURCE, source_file)
        dest_path = os.path.join(WIKI_TEMP, dest_file)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"   ✅ Copied {source_file} → {dest_file}")
            copied_files += 1
        else:
            print(f"   ⚠️  Warning: {source_file} not found")
    
    print(f"\n📊 Copied {copied_files} files to wiki repository")
    
    print("\n🔄 Step 3: Committing and pushing changes...")
    
    # Change to wiki directory
    os.chdir(WIKI_TEMP)
    
    # Configure git if needed
    run_command("git config user.name 'CloudViz Wiki Bot'")
    run_command("git config user.email 'wiki@cloudviz.com'")
    
    # Add all files
    if not run_command("git add ."):
        print("❌ Failed to add files to git")
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("ℹ️  No changes to commit - wiki is already up to date!")
        os.chdir("..")
        shutil.rmtree(WIKI_TEMP)
        return True
    
    # Commit changes
    commit_message = f"feat: Deploy comprehensive CloudViz wiki documentation\\n\\n- Added {copied_files} documentation pages\\n- Complete API reference and guides\\n- Enterprise-grade documentation\\n\\nAuto-deployed from CloudViz repository"
    
    if not run_command(f'git commit -m "{commit_message}"'):
        print("❌ Failed to commit changes")
        return False
    
    # Push changes
    if not run_command("git push origin master"):
        print("❌ Failed to push changes to wiki")
        return False
    
    print("✅ Wiki deployed successfully!")
    
    # Clean up
    os.chdir("..")
    shutil.rmtree(WIKI_TEMP)
    
    print("\n🎉 Deployment Complete!")
    print("=" * 50)
    print("📖 Your wiki is now live at:")
    print("   https://github.com/navidrast/cloudviz/wiki")
    print("\n📚 Available pages:")
    for source_file in file_mapping.keys():
        if os.path.exists(os.path.join(WIKI_SOURCE, source_file)):
            page_name = source_file.replace('.md', '').replace('-', ' ')
            print(f"   - {page_name}")
    
    return True

if __name__ == "__main__":
    success = deploy_wiki()
    sys.exit(0 if success else 1)
