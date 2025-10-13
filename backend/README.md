# 🔧 Backend - DreamAIry API Services

This directory contains the backend API services for DreamAIry.

## 🚀 Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Run tests
python test_demo.py
```

## 📁 Structure

```
backend/
├── api/                   # API endpoints
├── services/              # Business logic
├── models/                # Data models
├── utils/                 # Utility functions
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
└── README.md
```

## 🎯 Key Features

- **RESTful API**: Clean API endpoints
- **AI Integration**: Story and image generation
- **Session Management**: User session handling
- **CORS Support**: Frontend integration
- **Error Handling**: Robust error management

## 🔧 API Endpoints

### Sessions
- `POST /api/v1/demo/sessions` - Create new session
- `POST /api/v1/demo/sessions/{id}/end` - End session

### Story Generation
- `POST /api/v1/demo/sessions/{id}/story` - Generate story segment
- `POST /api/v1/demo/sessions/{id}/emotion` - Send emotion feedback

### Image Generation
- `POST /api/v1/demo/sessions/{id}/generate-image` - Generate story image
- `POST /api/v1/demo/sessions/{id}/photo` - Upload user photo

### System
- `GET /api/v1/system/status` - System health check

## 🌐 Environment Variables

Create a `.env` file:

```bash
FLASK_ENV=development
FLASK_DEBUG=True
PORT=3001
CORS_ORIGINS=http://localhost:3000
AI_API_KEY=your_api_key_here
```

## 🤖 AI Services Integration

The backend integrates with various AI services:

- **OpenAI**: Story generation
- **Stability AI**: Image generation
- **Local AI**: Fallback services
- **Emotion AI**: Emotion detection

## 🔍 Testing

```bash
# Run all tests
python test_demo.py

# Test specific service
python test_ai_services.py

# Check server status
python check_server.py
```

## 📊 Monitoring

- Health check endpoint
- Request logging
- Error tracking
- Performance metrics

## 🔒 Security

- CORS configuration
- Input validation
- Rate limiting
- Secure headers