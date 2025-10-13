#!/usr/bin/env python3
"""
Start only backend - for when npm has issues
"""

import os
import sys
import subprocess

def main():
    print("=" * 50)
    print("DreamAIry Backend Only Starter")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("ERROR: Please run this script from the DreamAIry project root directory")
        print("Expected structure:")
        print("  DreamAIry/")
        print("  ├── backend/")
        print("  └── start_backend_only.py")
        input("Press Enter to exit...")
        return
    
    print(f"Python: {sys.version}")
    print("Starting backend server...")
    print("Backend will be available at: http://localhost:3001")
    print()
    print("To access the app:")
    print("1. Backend API: http://localhost:3001")
    print("2. Admin Panel: Open admin_panel_working.html")
    print("3. For full app, start frontend separately")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    backend_path = os.path.join(os.getcwd(), 'backend')
    
    try:
        subprocess.run([sys.executable, 'app.py'], cwd=backend_path)
    except KeyboardInterrupt:
        print("\nBackend stopped by user")
    except Exception as e:
        print(f"Backend error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()