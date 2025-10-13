# 🌟 DreamAIry - Adaptive AI Storytelling Platform

> **Neural Ninjas Avengers** | Professional AI-Powered Children's Storytelling Application

[![Neural Ninjas Avengers](https://img.shields.io/badge/Neural%20Ninjas%20Avengers-Project-blue?style=for-the-badge&logo=github)](https://github.com/Neural-Ninjas-Avengers)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)](https://python.org/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/bedrock/)

## 📖 Overview

DreamAIry is an enterprise-grade, AI-powered storytelling platform that creates personalized, adaptive stories for children. Using cutting-edge AI technology from AWS Bedrock, the platform generates unique narratives, custom illustrations, and natural voice narration that adapt in real-time to children's emotions and preferences.

### 🎯 Key Features

- **🎭 Adaptive Storytelling**: AI-generated stories with narrative continuity that adapt to user preferences
- **📸 Personalized Avatars**: Transform user photos into storybook characters using AWS Titan Image Generator
- **🎨 AI Illustrations**: Automatic story illustrations with IMAGE_VARIATION technology
- **🗣️ Multi-Voice Narration**: AWS Polly with 10+ professional voices (Spanish & English)
- **😊 Emotion Detection**: Real-time emotion analysis using AWS Rekognition
- **🌍 Bilingual Support**: Full Spanish and English interface
- **🎵 Audio Controls**: Professional audio playback with voice selection and volume control
- **📱 Responsive Design**: Modern glassmorphism UI that works on all devices

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **AWS Account** (optional, for production features)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Neural-Ninjas-Avengers/dreamairy.git
cd dreamairy
```

2. **Install backend dependencies**:
```bash
pip install -r backend/requirements.txt
```

3. **Install frontend dependencies**:
```bash
cd frontend
npm install
cd ..
```

4. **Start the application**:
```bash
# Option A: Start everything at once (recommended)
python start_dreamairy.py

# Option B: Start components separately
python backend/app.py          # Terminal 1: Backend (port 3001)
cd frontend && npm start       # Terminal 2: Frontend (port 3000)
```

5. **Access the application**:
- **Main App**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **Admin Panel**: Open `admin/simple-admin.html` in browser

## 🏗️ Architecture

### Technology Stack

**Frontend**:
- React 18+ with Hooks
- Framer Motion for animations
- Modern CSS with Glassmorphism
- Responsive design (mobile-first)

**Backend**:
- Python Flask REST API
- AWS Bedrock integration
- AWS Polly for TTS
- AWS Rekognition for emotion detection
- AWS Titan for image generation

**AI Services**:
- **Text Generation**: Amazon Bedrock (Claude 3 Haiku / Titan Text)
- **Image Generation**: Amazon Titan Image Generator
- **Voice Synthesis**: Amazon Polly (Neural voices)
- **Emotion Analysis**: Amazon Rekognition
- **Fallback Systems**: Local templates and SVG generation

### Project Structure

```
dreamairy/
├── backend/                    # Python Flask backend
│   ├── admin/                  # Admin module & AWS integration
│   │   ├── aws_connector.py    # AWS Bedrock/Polly/Rekognition
│   │   ├── config_manager.py   # Configuration management
│   │   └── api.py              # Admin API endpoints
│   ├── api/                    # API endpoints
│   ├── core/                   # Core business logic
│   │   ├── story_generator.py  # Story generation engine
│   │   ├── story_orchestrator.py # Story orchestration
│   │   └── emotion_analyzer.py # Emotion detection
│   ├── services/               # Service layer
│   │   ├── avatar_fallback_controller.py # Avatar generation
│   │   ├── aws_prompt_generator.py # Prompt engineering
│   │   └── dynamic_client_selector.py # Client selection
│   ├── models/                 # Data models
│   └── app.py                  # Main Flask application
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ModernStoryArea.js # Main story interface
│   │   │   ├── AudioControls.js # Audio playback controls
│   │   │   ├── PhotoCapture.js # Photo capture & avatar
│   │   │   └── EmotionDetector.js # Emotion detection
│   │   ├── services/           # Frontend services
│   │   │   └── StorytellingService.js # API client
│   │   ├── contexts/           # React contexts
│   │   └── App.js              # Main application
│   └── package.json
├── admin/                      # Admin panel
│   ├── simple-admin.html       # Admin interface
│   └── control_server.py       # Admin server
├── .kiro/                      # Kiro IDE specifications
│   └── specs/                  # Feature specifications
│       ├── adaptive-storytelling-agent/
│       ├── avatar-enhancement/
│       └── admin-module/
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── start_dreamairy.py          # Main launcher
├── check_system.py             # System verification
└── README.md                   # This file
```

## ⚙️ Configuration

### Demo Mode (Default)

Perfect for development and testing:
- ✅ No AWS costs
- ✅ Local story templates
- ✅ SVG fallback illustrations
- ✅ Browser TTS for audio

### Production Mode

For full AI capabilities:

1. **Open Admin Panel**: `admin/simple-admin.html`
2. **Configure AWS**:
   - Set environment to "Production" or "Staging"
   - Enter AWS Access Key ID
   - Enter AWS Secret Access Key
   - Select AWS Region (default: eu-west-1)
   - Enable AWS services
3. **Save Configuration**
4. **Restart Backend**: `python backend/app.py`

### AWS Services Configuration

**Required AWS Services**:
- Amazon Bedrock (Text & Image generation)
- Amazon Polly (Text-to-speech)
- Amazon Rekognition (Emotion detection)

**Estimated Costs** (per 1000 requests):
- Story generation: ~$0.50
- Image generation: ~$2.00
- Voice synthesis: ~$0.20
- Emotion detection: ~$1.00

## 🎨 Features in Detail

### 1. Adaptive Storytelling

- **Narrative Continuity**: Each story segment builds on previous ones
- **Context Awareness**: Maintains characters, settings, and plot across segments
- **Age-Appropriate**: Content tailored to child's age (3-12 years)
- **Theme Selection**: Fantasy, adventure, animals, friendship
- **Emotional Goals**: Calm, entertain, or stimulate play

### 2. Personalized Avatars

- **Photo Upload**: Capture or upload user photo
- **AI Transformation**: AWS Titan converts photo to storybook character
- **IMAGE_VARIATION**: Uses photo as base for avatar generation
- **Consistent Character**: Same avatar appears in all illustrations
- **Fallback System**: Template avatars if AWS unavailable

### 3. AI Illustrations

- **Automatic Generation**: Illustrations created for each story segment
- **Avatar Integration**: User's avatar included in story scenes
- **IMAGE_VARIATION**: Creates scenes based on avatar/photo
- **Retry Strategy**: Multiple attempts with progressively safer prompts
- **SVG Fallback**: Enhanced SVG generation if AWS blocked

### 4. Voice Narration

- **AWS Polly Integration**: Professional neural voices
- **Voice Selection**: 10+ voices (5 Spanish, 5 English)
- **Audio Controls**: Play, stop, volume, speed
- **Voice Preview**: Test voices before selection
- **Browser Fallback**: Browser TTS if AWS unavailable

### 5. Emotion Detection

- **Photo Analysis**: AWS Rekognition detects emotions
- **Real-time Adaptation**: Story adapts to detected emotions
- **Multiple Emotions**: Joy, sadness, excitement, calm, etc.
- **Confidence Scoring**: Only acts on high-confidence detections

## 🧪 Testing

### System Verification

```bash
python check_system.py
```

### Component Tests

```bash
# Test AWS avatar generation
python test_direct_aws_avatar.py

# Test audio system
python test_audio_system.py

# Test story continuity
python test_story_with_avatar.py

# Test image generation
python test_image_generation.py
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 API Documentation

### Main Endpoints

**Session Management**:
- `POST /api/v1/demo/sessions` - Create new session
- `POST /api/v1/demo/sessions/{id}/end` - End session

**Story Generation**:
- `POST /api/v1/demo/sessions/{id}/story` - Generate story segment
- `POST /api/v1/demo/sessions/{id}/emotion` - Send emotion feedback

**Media Generation**:
- `POST /api/v1/demo/sessions/{id}/upload-photo` - Upload photo & generate avatar
- `POST /api/v1/demo/sessions/{id}/generate-image` - Generate story illustration
- `POST /api/v1/demo/sessions/{id}/text-to-speech` - Generate audio

**Configuration**:
- `GET /api/v1/ai-info/current` - Get AI service status
- `GET /api/v1/demo/available-voices` - Get available voices

## 🔒 Security & Privacy

- **No Data Storage**: Photos processed in-memory only
- **AWS Encryption**: All AWS communications encrypted
- **Anonymous Sessions**: No personal data collected
- **COPPA Compliant**: Designed for children's privacy
- **Content Filtering**: AWS Responsible AI Policy enforced

## 🚀 Deployment

### Production Checklist

- [ ] Configure AWS credentials in admin panel
- [ ] Set environment to "Production"
- [ ] Enable AWS services
- [ ] Test all features with real AWS
- [ ] Configure CORS for production domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure environment variables
- [ ] Set up monitoring and logging
- [ ] Test fallback systems
- [ ] Verify content filtering

### Environment Variables

```bash
# Backend
FLASK_ENV=production
AWS_REGION=eu-west-1
CORS_ORIGINS=https://yourdomain.com

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AWS Bedrock** for powerful AI capabilities
- **React** for modern UI framework
- **Framer Motion** for smooth animations
- **Neural Ninjas Avengers** team for development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Neural-Ninjas-Avengers/dreamairy/issues)
- **Documentation**: [docs/](docs/)
- **Email**: support@dreamairy.com

## 🥷 About Neural Ninjas Avengers

DreamAIry is developed by **Neural Ninjas Avengers**, an organization dedicated to creating innovative AI-powered applications for education and creativity.

### Our Mission

To leverage cutting-edge AI technology to create magical, educational experiences for children worldwide.

---

**Made with ❤️ by Neural Ninjas Avengers** 🥷🦸‍♂️

*Creating magical stories for children, one AI-generated tale at a time* ✨📚
