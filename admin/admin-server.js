/**
 * Kiro Admin Server - Real Command Execution
 * Node.js server that actually starts/stops Python and React servers
 */

const express = require('express');
const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Global process tracking
let processes = {
    python: null,
    react: null
};

// Paths configuration
const PATHS = {
    python: 'C:\\Users\\fernando.bori\\AppData\\Local\\Programs\\Python\\Python313\\python.exe',
    node: 'C:\\node-v22.19.0-win-x64\\node.exe',
    npm: 'C:\\node-v22.19.0-win-x64\\npm.cmd',
    projectRoot: path.resolve(__dirname, '..'),
    backendRoot: path.resolve(__dirname, '..', 'backend'),
    frontendRoot: path.resolve(__dirname, '..', 'frontend')
};

// Utility functions
function isProcessRunning(pid) {
    try {
        process.kill(pid, 0);
        return true;
    } catch (e) {
        return false;
    }
}

function killProcess(proc) {
    if (proc && proc.pid && isProcessRunning(proc.pid)) {
        try {
            if (process.platform === 'win32') {
                exec(`taskkill /pid ${proc.pid} /t /f`, (error) => {
                    if (error) console.log('Error killing process:', error);
                });
            } else {
                proc.kill('SIGTERM');
            }
            return true;
        } catch (error) {
            console.error('Error killing process:', error);
            return false;
        }
    }
    return false;
}

// API Routes

// Get system status
app.get('/api/status', (req, res) => {
    const status = {
        python: {
            running: processes.python && isProcessRunning(processes.python.pid),
            pid: processes.python ? processes.python.pid : null
        },
        react: {
            running: processes.react && isProcessRunning(processes.react.pid),
            pid: processes.react ? processes.react.pid : null
        },
        timestamp: new Date().toISOString()
    };
    
    res.json(status);
});

// Start Python server
app.post('/api/start/python', (req, res) => {
    if (processes.python && isProcessRunning(processes.python.pid)) {
        return res.json({ 
            success: false, 
            message: 'Python server is already running',
            pid: processes.python.pid 
        });
    }

    try {
        console.log('Starting Python server...');
        
        const pythonProcess = spawn(PATHS.python, [
            'app.py'
        ], {
            cwd: PATHS.backendRoot,
            detached: false,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        processes.python = pythonProcess;

        pythonProcess.stdout.on('data', (data) => {
            console.log(`Python stdout: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.log(`Python stderr: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
            processes.python = null;
        });

        pythonProcess.on('error', (error) => {
            console.error('Python process error:', error);
            processes.python = null;
        });

        res.json({ 
            success: true, 
            message: 'Python server starting...', 
            pid: pythonProcess.pid 
        });

    } catch (error) {
        console.error('Error starting Python server:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to start Python server: ' + error.message 
        });
    }
});

// Stop Python server
app.post('/api/stop/python', (req, res) => {
    if (!processes.python || !isProcessRunning(processes.python.pid)) {
        return res.json({ 
            success: false, 
            message: 'Python server is not running' 
        });
    }

    try {
        const killed = killProcess(processes.python);
        processes.python = null;
        
        res.json({ 
            success: killed, 
            message: killed ? 'Python server stopped' : 'Failed to stop Python server' 
        });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            message: 'Error stopping Python server: ' + error.message 
        });
    }
});

// Start React server
app.post('/api/start/react', (req, res) => {
    if (processes.react && isProcessRunning(processes.react.pid)) {
        return res.json({ 
            success: false, 
            message: 'React server is already running',
            pid: processes.react.pid 
        });
    }

    try {
        console.log('Starting React server...');
        
        const reactProcess = spawn(PATHS.npm, ['start'], {
            cwd: PATHS.frontendRoot,
            detached: false,
            stdio: ['pipe', 'pipe', 'pipe'],
            shell: true
        });

        processes.react = reactProcess;

        reactProcess.stdout.on('data', (data) => {
            console.log(`React stdout: ${data}`);
        });

        reactProcess.stderr.on('data', (data) => {
            console.log(`React stderr: ${data}`);
        });

        reactProcess.on('close', (code) => {
            console.log(`React process exited with code ${code}`);
            processes.react = null;
        });

        reactProcess.on('error', (error) => {
            console.error('React process error:', error);
            processes.react = null;
        });

        res.json({ 
            success: true, 
            message: 'React server starting...', 
            pid: reactProcess.pid 
        });

    } catch (error) {
        console.error('Error starting React server:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to start React server: ' + error.message 
        });
    }
});

// Stop React server
app.post('/api/stop/react', (req, res) => {
    if (!processes.react || !isProcessRunning(processes.react.pid)) {
        return res.json({ 
            success: false, 
            message: 'React server is not running' 
        });
    }

    try {
        const killed = killProcess(processes.react);
        processes.react = null;
        
        res.json({ 
            success: killed, 
            message: killed ? 'React server stopped' : 'Failed to stop React server' 
        });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            message: 'Error stopping React server: ' + error.message 
        });
    }
});

// Start all servers
app.post('/api/start/all', async (req, res) => {
    try {
        const results = [];
        
        // Start Python first
        if (!processes.python || !isProcessRunning(processes.python.pid)) {
            const pythonResult = await new Promise((resolve) => {
                const pythonProcess = spawn(PATHS.python, [
                    'app.py'
                ], {
                    cwd: PATHS.backendRoot,
                    detached: false,
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                processes.python = pythonProcess;
                
                pythonProcess.on('error', (error) => {
                    resolve({ service: 'python', success: false, error: error.message });
                });
                
                setTimeout(() => {
                    resolve({ service: 'python', success: true, pid: pythonProcess.pid });
                }, 2000);
            });
            
            results.push(pythonResult);
        }

        // Wait a bit, then start React
        setTimeout(() => {
            if (!processes.react || !isProcessRunning(processes.react.pid)) {
                const reactProcess = spawn(PATHS.npm, ['start'], {
                    cwd: PATHS.frontendRoot,
                    detached: false,
                    stdio: ['pipe', 'pipe', 'pipe'],
                    shell: true
                });

                processes.react = reactProcess;
                results.push({ service: 'react', success: true, pid: reactProcess.pid });
            }
        }, 3000);

        res.json({ 
            success: true, 
            message: 'Starting all servers...', 
            results: results 
        });

    } catch (error) {
        res.status(500).json({ 
            success: false, 
            message: 'Error starting servers: ' + error.message 
        });
    }
});

// Stop all servers
app.post('/api/stop/all', (req, res) => {
    try {
        const results = [];
        
        if (processes.python) {
            const pythonKilled = killProcess(processes.python);
            processes.python = null;
            results.push({ service: 'python', stopped: pythonKilled });
        }
        
        if (processes.react) {
            const reactKilled = killProcess(processes.react);
            processes.react = null;
            results.push({ service: 'react', stopped: reactKilled });
        }

        res.json({ 
            success: true, 
            message: 'Stopping all servers...', 
            results: results 
        });

    } catch (error) {
        res.status(500).json({ 
            success: false, 
            message: 'Error stopping servers: ' + error.message 
        });
    }
});

// Cleanup on exit
process.on('SIGINT', () => {
    console.log('Shutting down admin server...');
    
    if (processes.python) {
        killProcess(processes.python);
    }
    
    if (processes.react) {
        killProcess(processes.react);
    }
    
    process.exit(0);
});

// Add health endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Admin server is running' });
});

// Redirect root to admin panel
app.get('/', (req, res) => {
    res.redirect('/index.html');
});

// Start the admin server
app.listen(PORT, () => {
    console.log(`🎮 Kiro Admin Server running on http://localhost:${PORT}`);
    console.log(`📁 Project root: ${PATHS.projectRoot}`);
    console.log(`⚛️ Frontend root: ${PATHS.frontendRoot}`);
    console.log(`🔧 Backend root: ${PATHS.backendRoot}`);
    console.log(`🐍 Python path: ${PATHS.python}`);
    console.log(`📦 Node path: ${PATHS.node}`);
    console.log('');
    console.log('🚀 Ready to manage servers!');
    console.log('💡 Open: http://localhost:3002 to access admin panel');
    console.log('🎮 Direct link: http://localhost:3002/real-admin.html');
});