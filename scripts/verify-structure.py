#!/usr/bin/env python3
"""
DreamAIry Structure Verification Script
Verifies that the new project structure is working correctly
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(item, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def check_directory_structure():
    """Check if all required directories exist"""
    print_header("🏗️ Directory Structure Check")
    
    required_dirs = [
        "frontend",
        "backend", 
        "admin",
        "docs",
        "scripts",
        ".github",
        ".kiro"
    ]
    
    all_good = True
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        print_status(f"Directory: {dir_name}", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_frontend():
    """Check frontend structure and dependencies"""
    print_header("🎨 Frontend Check")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/src/App.js",
        "frontend/src/components/ModernWelcomeScreen.js",
        "frontend/src/components/ModernStoryArea.js",
        "frontend/src/services/StorytellingService.js"
    ]
    
    all_good = True
    for file_path in frontend_files:
        exists = os.path.exists(file_path)
        print_status(f"File: {file_path}", exists)
        if not exists:
            all_good = False
    
    # Check if node_modules exists
    node_modules = os.path.exists("frontend/node_modules")
    print_status("Dependencies installed", node_modules, 
                "Run 'cd frontend && npm install' if missing")
    
    return all_good

def check_backend():
    """Check backend structure"""
    print_header("🔧 Backend Check")
    
    backend_files = [
        "backend/main.py",
        "backend/config.py"
    ]
    
    all_good = True
    for file_path in backend_files:
        exists = os.path.exists(file_path)
        print_status(f"File: {file_path}", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_admin():
    """Check admin panel structure"""
    print_header("👨‍💼 Admin Panel Check")
    
    admin_files = [
        "admin/package.json",
        "admin/admin-server.js",
        "admin/index.html"
    ]
    
    all_good = True
    for file_path in admin_files:
        exists = os.path.exists(file_path)
        print_status(f"File: {file_path}", exists)
        if not exists:
            all_good = False
    
    # Check admin dependencies
    admin_modules = os.path.exists("admin/node_modules")
    print_status("Admin dependencies installed", admin_modules,
                "Run 'cd admin && npm install' if missing")
    
    return all_good

def check_scripts():
    """Check utility scripts"""
    print_header("🔧 Scripts Check")
    
    script_files = [
        "scripts/start_everything.bat",
        "scripts/start_admin.bat", 
        "scripts/check_server.py",
        "scripts/test_demo.py"
    ]
    
    all_good = True
    for file_path in script_files:
        exists = os.path.exists(file_path)
        print_status(f"Script: {file_path}", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_documentation():
    """Check documentation structure"""
    print_header("📚 Documentation Check")
    
    doc_files = [
        "README.md",
        "SETUP.md",
        "CONTRIBUTING.md",
        "docs/README.md",
        "frontend/README.md",
        "backend/README.md"
    ]
    
    all_good = True
    for file_path in doc_files:
        exists = os.path.exists(file_path)
        print_status(f"Documentation: {file_path}", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_configuration():
    """Check configuration files"""
    print_header("⚙️ Configuration Check")
    
    config_files = [
        "package.json",
        ".gitignore",
        ".github/workflows/ci.yml",
        "LICENSE"
    ]
    
    all_good = True
    for file_path in config_files:
        exists = os.path.exists(file_path)
        print_status(f"Config: {file_path}", exists)
        if not exists:
            all_good = False
    
    return all_good

def check_old_structure():
    """Check if old structure still exists"""
    print_header("🧹 Cleanup Check")
    
    old_paths = [
        "adaptive-storytelling-agent"
    ]
    
    cleanup_needed = False
    for path in old_paths:
        exists = os.path.exists(path)
        if exists:
            print_status(f"Old directory: {path}", False, "Should be removed")
            cleanup_needed = True
        else:
            print_status(f"Old directory cleaned: {path}", True)
    
    return not cleanup_needed

def run_quick_tests():
    """Run quick functionality tests"""
    print_header("🧪 Quick Tests")
    
    # Test package.json scripts
    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)
        
        required_scripts = ["start", "build", "install-deps"]
        scripts_ok = all(script in package_data.get("scripts", {}) for script in required_scripts)
        print_status("Package.json scripts", scripts_ok)
        
    except Exception as e:
        print_status("Package.json scripts", False, str(e))
        scripts_ok = False
    
    # Test frontend package.json
    try:
        with open("frontend/package.json", "r") as f:
            frontend_package = json.load(f)
        
        has_react = "react" in frontend_package.get("dependencies", {})
        print_status("Frontend React dependency", has_react)
        
    except Exception as e:
        print_status("Frontend package.json", False, str(e))
        has_react = False
    
    return scripts_ok and has_react

def main():
    """Main verification function"""
    print_header("🌟 DreamAIry Structure Verification")
    print("Checking project structure after reorganization...")
    
    # Change to project root if we're in scripts directory
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Frontend", check_frontend),
        ("Backend", check_backend), 
        ("Admin Panel", check_admin),
        ("Scripts", check_scripts),
        ("Documentation", check_documentation),
        ("Configuration", check_configuration),
        ("Cleanup Status", check_old_structure),
        ("Quick Tests", run_quick_tests)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"Error in {check_name}", False, str(e))
            results.append((check_name, False))
    
    # Summary
    print_header("📊 Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        print_status(check_name, result)
    
    print(f"\n🎯 Overall Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Excellent! Project structure is perfect!")
        print("✅ Ready for development and GitHub upload")
    elif passed >= total * 0.8:
        print("\n👍 Good! Minor issues to fix")
        print("🔧 Address the failed checks above")
    else:
        print("\n⚠️ Issues detected that need attention")
        print("🛠️ Please fix the failed checks before proceeding")
    
    print("\n🚀 Next steps:")
    print("1. Fix any failed checks")
    print("2. Run 'npm run install-deps' to install dependencies")
    print("3. Test with 'npm run dev:all'")
    print("4. Commit and push to GitHub")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)