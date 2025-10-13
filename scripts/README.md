# 🔧 Scripts - DreamAIry Utilities

This directory contains utility scripts for development, testing, and deployment.

## 📁 Available Scripts

### 🚀 **Startup Scripts**
- `start_everything.bat` - Start all services (frontend + backend)
- `start_server.bat` - Start only the backend server
- `start_admin.bat` - Start the admin panel
- `open_demo.bat` - Open demo in browser
- `open_admin.bat` - Open admin panel in browser
- `quick_admin.bat` - Quick admin panel access

### 🧪 **Testing Scripts**
- `test_demo.py` - Test the demo functionality
- `test_ai_services.py` - Test AI service integration
- `test_illustrations.py` - Test image generation
- `check_server.py` - Check server health and status

### 🌐 **Debug Tools**
- `debug_demo.html` - Debug demo interface
- `debug_simple.html` - Simple debug interface

## 🚀 Usage Examples

### Start Development Environment
```bash
# Windows
scripts/start_everything.bat

# Manual (cross-platform)
cd frontend && npm start &
cd backend && python app.py &
```

### Run Tests
```bash
# Test all services
python scripts/test_demo.py

# Test specific AI services
python scripts/test_ai_services.py

# Check server status
python scripts/check_server.py
```

### Debug Issues
```bash
# Open debug interface
open scripts/debug_demo.html

# Check server health
python scripts/check_server.py
```

## 🔧 Script Details

### `start_everything.bat`
Starts both frontend and backend services simultaneously.
- Opens frontend on http://localhost:3000
- Starts backend on http://localhost:3001
- Handles dependencies automatically

### `test_demo.py`
Comprehensive testing script for demo functionality.
- Tests API endpoints
- Validates AI services
- Checks image generation
- Reports test results

### `check_server.py`
Health check utility for backend services.
- Verifies server connectivity
- Tests API endpoints
- Checks AI service status
- Provides diagnostic information

### `test_ai_services.py`
Specialized testing for AI integrations.
- Tests story generation
- Validates image creation
- Checks emotion detection
- Performance benchmarking

## 🌍 Cross-Platform Compatibility

### Windows (.bat files)
- `start_everything.bat`
- `start_server.bat`
- `open_demo.bat`
- `quick_admin.bat`

### Unix/Linux/Mac (Python scripts)
- `test_demo.py`
- `test_ai_services.py`
- `check_server.py`
- `test_illustrations.py`

## 📝 Creating New Scripts

When adding new scripts:

1. **Choose the right type**:
   - `.bat` for Windows automation
   - `.py` for cross-platform utilities
   - `.html` for debug interfaces

2. **Follow naming conventions**:
   - Use descriptive names
   - Include action verb (start, test, check)
   - Use underscores for separation

3. **Add documentation**:
   - Include header comments
   - Explain parameters
   - Provide usage examples

4. **Test thoroughly**:
   - Test on target platforms
   - Handle error cases
   - Provide helpful output

## 🔍 Troubleshooting

### Common Issues

**Script won't run:**
- Check file permissions
- Verify Python/Node.js installation
- Check path dependencies

**Services won't start:**
- Check port availability
- Verify dependencies installed
- Check environment variables

**Tests failing:**
- Ensure services are running
- Check network connectivity
- Verify API keys and configuration

### Getting Help

1. Run `check_server.py` for diagnostics
2. Check script output for error messages
3. Verify all dependencies are installed
4. Consult the main documentation

---

**Make development easier with automation!** 🚀⚡