# 🎮 Kiro Admin Panel - Master Control Center

Professional dashboard for managing the complete Kiro Storytelling Agent stack (Python Backend + React Frontend).

## 🚀 Features

### **Dual Server Management**
- **Python Backend Control**: Start, stop, restart the FastAPI server (Port 3001)
- **React Frontend Control**: Start, stop, restart the React development server (Port 3000)
- **Master Control**: Start/stop everything with one click
- **Auto-coordination**: Automatically start React after Python (configurable)

### **Real-time Monitoring**
- Live server status indicators
- System metrics and uptime tracking
- Active session monitoring
- Service health checks

### **Advanced Controls**
- **Configuration Management**: Toggle demo mode, offline mode, mock services
- **Session Management**: View, monitor, and terminate active storytelling sessions
- **System Logs**: Real-time log viewing with filtering and export
- **Service Status**: Monitor API, WebSocket, and AWS service health

## 🎯 Quick Start Guide

### **Method 1: Everything at Once (Recommended)**
```bash
# Double-click this file to start everything:
start_everything.bat
```
This will:
1. ✅ Check all dependencies
2. 🐍 Start Python Backend (Port 3001)
3. ⚛️ Start React Frontend (Port 3000)
4. 🎮 Open Admin Panel automatically

### **Method 2: Individual Control**
1. **Start Python Backend**:
   ```bash
   # Double-click:
   start_server.bat
   ```

2. **Start React Frontend**:
   ```bash
   # Double-click:
   react-demo/start_react.bat
   ```

3. **Open Admin Panel**:
   ```bash
   # Double-click:
   admin/index.html
   ```

### **Method 3: Manual Control**
Use the Admin Panel buttons to start services individually with detailed instructions.

## 🌐 Service URLs

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **React App** | http://localhost:3000 | Main storytelling interface |
| **Python API** | http://localhost:3001 | Backend API server |
| **API Docs** | http://localhost:3001/docs | Interactive API documentation |
| **Health Check** | http://localhost:3001/health | Server health status |
| **Admin Panel** | file:///.../admin/index.html | This control panel |

## 🎮 Admin Panel Sections

### **1. Server Control Cards**
- **Python Backend**: Control FastAPI server (Port 3001)
- **React Frontend**: Control React dev server (Port 3000)
- **Master Control**: Start/stop everything with one button

### **2. System Metrics**
- Active storytelling sessions
- Total API requests processed
- WebSocket connections
- System uptime

### **3. Configuration**
- **Demo Mode**: Enable/disable demo features
- **Offline Mode**: Use mock services (no AWS costs) ✅ Recommended
- **Mock Services**: Toggle between real and mock AWS services
- **Auto-start React**: Automatically start React after Python

### **4. Service Status**
- **API REST**: Backend API availability
- **WebSocket**: Real-time communication status
- **AWS Services**: Real vs Mock mode indicator
- **Demo Interface**: Frontend availability

### **5. Active Sessions**
- View all active storytelling sessions
- Monitor session duration and status
- Terminate individual or all sessions
- Session details and engagement metrics

### **6. System Logs**
- Real-time log streaming from both servers
- Filter by log level (info, warning, error, debug)
- Export logs to file
- Auto-scroll toggle
- Clear logs functionality

## ⚙️ Configuration Options

### **Recommended Settings for Development**
- ✅ **Demo Mode**: ON (enables sample data and features)
- ✅ **Offline Mode**: ON (no AWS costs, uses mock services)
- ✅ **Mock Services**: ON (safe for development)
- ✅ **Auto-start React**: ON (convenience feature)

### **Production Settings**
- ❌ **Demo Mode**: OFF
- ❌ **Offline Mode**: OFF (if using real AWS)
- ❌ **Mock Services**: OFF (if using real AWS)
- ⚠️ **Note**: Real AWS mode will incur costs

## 🔧 Troubleshooting

### **Python Server Won't Start**
1. ✅ Check Python path: `C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Check port 3001 availability
4. ✅ Review logs in admin panel

### **React Server Won't Start**
1. ✅ Check Node.js path: `C:\node-v22.19.0-win-x64\node.exe`
2. ✅ Install dependencies: `npm install` in react-demo folder
3. ✅ Check port 3000 availability
4. ✅ Review terminal output

### **Admin Panel Issues**
1. ✅ Open HTML file directly (file:// protocol)
2. ✅ Check browser console for errors
3. ✅ Ensure servers are running for full functionality
4. ✅ Try refreshing the page

### **Services Not Responding**
1. ✅ Check server status indicators in admin panel
2. ✅ Verify firewall settings allow localhost connections
3. ✅ Ensure no other services use ports 3000/3001
4. ✅ Restart services using admin panel buttons

## 🛠️ Development

### **Architecture**
```
Kiro Storytelling Agent
├── Python Backend (FastAPI)     # Port 3001
│   ├── REST API endpoints
│   ├── WebSocket communication
│   └── Story generation logic
├── React Frontend (React+Tailwind) # Port 3000
│   ├── Modern UI components
│   ├── Real-time story interface
│   └── Emotion selection
└── Admin Panel (Vanilla JS)     # File-based
    ├── Server control
    ├── Monitoring dashboard
    └── Configuration management
```

### **File Structure**
```
adaptive-storytelling-agent/
├── start_everything.bat          # 🚀 Master startup script
├── start_server.bat             # 🐍 Python server only
├── react-demo/
│   ├── start_react.bat          # ⚛️ React server only
│   └── src/                     # React components
└── admin/
    ├── index.html               # 🎮 Admin dashboard
    ├── admin.js                 # Dashboard logic
    └── README.md                # This file
```

### **Adding New Features**
1. **Server Control**: Modify `admin.js` server management functions
2. **UI Components**: Update `index.html` dashboard layout
3. **Monitoring**: Add new metrics in `updateMetrics()` function
4. **Configuration**: Add toggles in configuration section

## 🎉 Success Indicators

When everything is working correctly, you should see:

- 🟢 **Python Backend**: Running (Port 3001)
- 🟢 **React Frontend**: Running (Port 3000)
- 🟢 **Master Status**: Full System Running
- 🟢 **API Status**: Active
- 🟢 **WebSocket**: Active
- 🟡 **AWS Services**: Mock Mode (No Costs)
- 🟢 **Demo Interface**: Active

## 📞 Support

If you encounter issues:
1. Check the **System Logs** section in admin panel
2. Review terminal outputs from both servers
3. Verify all dependencies are installed
4. Ensure ports 3000 and 3001 are available
5. Try the **Master Control** restart function