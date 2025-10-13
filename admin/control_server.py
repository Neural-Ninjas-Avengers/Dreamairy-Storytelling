#!/usr/bin/env python3
"""
DreamAIry Control Server
Manages backend and frontend processes via web API
"""

import subprocess
import psutil
import json
import os
import sys
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global process tracking
processes = {
    'backend': None,
    'frontend': None
}

def find_process_by_port(port):
    """Find process running on specific port"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Get connections for this process
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def kill_process_tree(pid):
    """Kill process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill children first
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        # Kill parent
        parent.terminate()
        
        # Wait for termination
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)
        
        # Force kill if still alive
        for proc in alive:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
                
        return True
    except psutil.NoSuchProcess:
        return True
    except Exception as e:
        print(f"Error killing process {pid}: {e}")
        return False

@app.route('/api/status')
def get_status():
    """Get status of all services"""
    backend_pid = find_process_by_port(3001)
    frontend_pid = find_process_by_port(3000)
    
    return jsonify({
        'backend': {
            'running': backend_pid is not None,
            'pid': backend_pid
        },
        'frontend': {
            'running': frontend_pid is not None,
            'pid': frontend_pid
        }
    })

@app.route('/api/start/backend', methods=['POST'])
def start_backend():
    """Start Python backend"""
    try:
        # Check if already running
        if find_process_by_port(3001):
            return jsonify({'success': False, 'message': 'Backend already running'})
        
        # Start backend process
        backend_dir = os.path.join(os.getcwd(), 'backend')
        if not os.path.exists(backend_dir):
            return jsonify({'success': False, 'message': 'Backend directory not found'})
        
        # Start process in background
        proc = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        processes['backend'] = proc
        
        # Wait a moment to check if it started successfully
        time.sleep(2)
        
        if find_process_by_port(3001):
            return jsonify({'success': True, 'message': 'Backend started successfully'})
        else:
            return jsonify({'success': False, 'message': 'Backend failed to start'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting backend: {str(e)}'})

@app.route('/api/stop/backend', methods=['POST'])
def stop_backend():
    """Stop Python backend"""
    try:
        backend_pid = find_process_by_port(3001)
        
        if not backend_pid:
            return jsonify({'success': False, 'message': 'Backend not running'})
        
        # Kill the process
        if kill_process_tree(backend_pid):
            processes['backend'] = None
            return jsonify({'success': True, 'message': 'Backend stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to stop backend'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping backend: {str(e)}'})

@app.route('/api/start/frontend', methods=['POST'])
def start_frontend():
    """Start React frontend"""
    try:
        # Check if already running
        if find_process_by_port(3000):
            return jsonify({'success': False, 'message': 'Frontend already running'})
        
        # Start frontend process
        frontend_dir = os.path.join(os.getcwd(), 'frontend')
        if not os.path.exists(frontend_dir):
            return jsonify({'success': False, 'message': 'Frontend directory not found'})
        
        # Check if npm is available
        try:
            result = subprocess.run(['npm', '--version'], check=True, capture_output=True, text=True, shell=True)
            logger.info(f"npm version detected: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"npm check failed: {e}")
            return jsonify({'success': False, 'message': 'npm not found. Install Node.js first.'})
        
        # Start process in background
        if os.name == 'nt':  # Windows
            proc = subprocess.Popen(
                ['cmd', '/c', 'npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=False
            )
        else:  # Unix/Linux/Mac
            proc = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        processes['frontend'] = proc
        
        return jsonify({'success': True, 'message': 'Frontend starting... (may take 30-60 seconds)'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting frontend: {str(e)}'})

@app.route('/api/stop/frontend', methods=['POST'])
def stop_frontend():
    """Stop React frontend"""
    try:
        frontend_pid = find_process_by_port(3000)
        
        if not frontend_pid:
            return jsonify({'success': False, 'message': 'Frontend not running'})
        
        # Kill the process
        if kill_process_tree(frontend_pid):
            processes['frontend'] = None
            return jsonify({'success': True, 'message': 'Frontend stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to stop frontend'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping frontend: {str(e)}'})

@app.route('/api/start/all', methods=['POST'])
def start_all():
    """Start both backend and frontend"""
    try:
        results = []
        
        # Start backend first
        backend_result = start_backend()
        results.append(f"Backend: {backend_result.get_json()['message']}")
        
        # Wait a moment
        time.sleep(3)
        
        # Start frontend
        frontend_result = start_frontend()
        results.append(f"Frontend: {frontend_result.get_json()['message']}")
        
        return jsonify({
            'success': True, 
            'message': 'Starting all services. ' + ' | '.join(results)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting all services: {str(e)}'})

@app.route('/api/stop/all', methods=['POST'])
def stop_all():
    """Stop both backend and frontend"""
    try:
        results = []
        
        # Stop frontend first
        frontend_result = stop_frontend()
        results.append(f"Frontend: {frontend_result.get_json()['message']}")
        
        # Stop backend
        backend_result = stop_backend()
        results.append(f"Backend: {backend_result.get_json()['message']}")
        
        return jsonify({
            'success': True, 
            'message': 'Stopped all services. ' + ' | '.join(results)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping all services: {str(e)}'})

@app.route('/api/restart/backend', methods=['POST'])
def restart_backend():
    """Restart backend"""
    try:
        stop_backend()
        time.sleep(2)
        return start_backend()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error restarting backend: {str(e)}'})

@app.route('/api/restart/frontend', methods=['POST'])
def restart_frontend():
    """Restart frontend"""
    try:
        stop_frontend()
        time.sleep(2)
        return start_frontend()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error restarting frontend: {str(e)}'})

@app.route('/api/health')
def health():
    """Health check for control server"""
    return jsonify({
        'status': 'healthy',
        'message': 'DreamAIry Control Server running',
        'port': 3002
    })

def cleanup_processes():
    """Cleanup processes on exit"""
    print("\n🛑 Cleaning up processes...")
    
    for name, proc in processes.items():
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ {name} process cleaned up")
            except:
                try:
                    proc.kill()
                    print(f"🔥 {name} process force killed")
                except:
                    pass

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    cleanup_processes()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🎮 DreamAIry Control Server")
    print("=" * 40)
    print("🌐 Starting control server on http://localhost:3002")
    print("📡 API available at http://localhost:3002/api/")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        app.run(host='0.0.0.0', port=3002, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Control server stopped by user")
    finally:
        cleanup_processes()