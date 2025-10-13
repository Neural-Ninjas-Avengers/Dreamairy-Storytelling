# 🎨 Frontend - DreamAIry React Application

This directory contains the React frontend application for DreamAIry.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 📁 Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ModernWelcomeScreen.js
│   │   ├── ModernStoryArea.js
│   │   ├── PhotoCapture.js
│   │   ├── EmotionDetector.js
│   │   └── ...
│   ├── services/          # API and AI services
│   │   ├── StorytellingService.js
│   │   ├── FreeAIStoryService.js
│   │   └── EmotionAnalysisService.js
│   ├── contexts/          # React contexts
│   │   └── LanguageContext.js
│   └── App.js             # Main application
├── public/                # Static assets
└── package.json
```

## 🎯 Key Features

- **Modern React**: Hooks, Context API, functional components
- **Responsive Design**: Mobile-first approach
- **Glassmorphism UI**: Premium visual design
- **Framer Motion**: Smooth animations
- **Multi-language**: Spanish/English support
- **AI Integration**: Story generation and emotion detection

## 🔧 Available Scripts

- `npm start` - Development server (http://localhost:3000)
- `npm run build` - Production build
- `npm test` - Run test suite
- `npm run lint` - Code linting
- `npm run format` - Code formatting

## 🌐 Environment Variables

Create a `.env` file:

```bash
REACT_APP_API_URL=http://localhost:3001
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎨 Design System

- **Colors**: Blue/indigo gradients with glassmorphism
- **Typography**: Modern, readable fonts
- **Animations**: Framer Motion powered
- **Responsive**: Mobile-first breakpoints

## 🤖 AI Integration

The frontend integrates with multiple AI services:

- **Story Generation**: Personalized storytelling
- **Image Generation**: Story illustrations
- **Emotion Detection**: Photo-based emotion analysis
- **Voice Synthesis**: Text-to-speech narration

## 🔍 Debugging

- React DevTools for component inspection
- Console logging for AI service calls
- Network tab for API requests
- Performance profiler for optimization