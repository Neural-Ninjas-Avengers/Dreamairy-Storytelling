#!/usr/bin/env python3
"""
DreamAIry Launcher - Simple script to start everything
"""

import subprocess
import sys
import time
import webbrowser
import os
from threading import Thread

def start_backend():
    """Start the Python backend"""
    print("🐍 Starting Python Backend...")
    try:
        # Get current directory and backend path
        current_dir = os.getcwd()
        backend_path = os.path.join(current_dir, 'backend')
        
        if not os.path.exists(backend_path):
            print(f"❌ Backend directory not found: {backend_path}")
            return
            
        # Start backend with proper working directory
        subprocess.run([sys.executable, 'app.py'], cwd=backend_path, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the React frontend"""
    print("⚛️ Starting React Frontend...")
    try:
        # Get current directory and frontend path
        current_dir = os.getcwd()
        frontend_path = os.path.join(current_dir, 'frontend')
        
        if not os.path.exists(frontend_path):
            print(f"❌ Frontend directory not found: {frontend_path}")
            print("💡 Make sure you're running this from the project root directory")
            return
            
        # Check if npm is available
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm not found. Please install Node.js first")
            print("💡 Download from: https://nodejs.org/")
            return
            
        # Check if node_modules exists
        node_modules_path = os.path.join(frontend_path, 'node_modules')
        if not os.path.exists(node_modules_path):
            print("📦 Installing dependencies first...")
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
            
        # Start frontend with proper working directory
        subprocess.run(['npm', 'start'], cwd=frontend_path, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        print("💡 Make sure you have Node.js installed and run 'npm install' first")

def start_control_server():
    """Start the control server"""
    print("🎮 Starting Control Server...")
    try:
        # Get current directory and admin path
        current_dir = os.getcwd()
        admin_path = os.path.join(current_dir, 'admin')
        
        if not os.path.exists(admin_path):
            print(f"❌ Admin directory not found: {admin_path}")
            return
            
        # Start control server with proper working directory
        subprocess.run([sys.executable, 'control_server.py'], cwd=admin_path, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Control server stopped by user")
    except Exception as e:
        print(f"❌ Control server error: {e}")

def main():
    print("🎮 DreamAIry Launcher")
    print("=" * 50)
    
    choice = input("""
Choose what to start:
1. Backend only (Python)
2. Frontend only (React)
3. Both (Full System)
4. Control Server + Admin Panel
5. Test Backend
6. Exit

Enter choice (1-6): """).strip()
    
    if choice == '1':
        start_backend()
    elif choice == '2':
        start_frontend()
    elif choice == '3':
        print("🚀 Starting Full System...")
        print("Backend will start first, then frontend in 5 seconds...")
        
        # Start backend in background thread
        backend_thread = Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a bit for backend to start
        time.sleep(5)
        
        # Start frontend
        start_frontend()
        
    elif choice == '4':
        print("🎮 Starting Control Server + Admin Panel...")
        print("Control server will start, then admin panel will open...")
        
        # Start control server in background
        control_thread = Thread(target=start_control_server, daemon=True)
        control_thread.start()
        
        # Wait for control server to start
        time.sleep(3)
        
        # Open admin panel
        import webbrowser
        admin_path = os.path.abspath('admin/simple-admin.html')
        webbrowser.open(f'file://{admin_path}')
        
        print("🌐 Admin panel opened in browser")
        print("🎮 Control server running on http://localhost:3002")
        print("🛑 Press Ctrl+C to stop control server")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Control server stopped")
        
    elif choice == '5':
        print("🧪 Testing Backend...")
        subprocess.run([sys.executable, 'scripts/quick_test.py'])
        
    elif choice == '6':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"❌ Launcher error: {e}")