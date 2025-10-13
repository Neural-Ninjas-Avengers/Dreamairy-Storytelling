# Adaptive Children's Storytelling Agent

An AI-powered system that generates and narrates personalized children's stories that adapt in real-time to emotional reactions.

## ⚠️ AWS Account Setup Required

**IMPORTANT**: This application uses AWS services. Before running:

1. **Set up AWS credentials** in `.env` file (copy from `.env.example`)
2. **Verify AWS account access** and ensure you have permissions for:
   - Amazon Bedrock (Claude/Titan models)
   - Amazon Transcribe
   - Amazon Rekognition
   - Amazon Polly
   - Amazon S3

3. **Check AWS billing** - This demo will incur AWS charges

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Start server**: 
   - **Easy way**: Double-click `start_server.bat`
   - **Manual way**: `python -m app.main`

5. **Access interfaces**:
   - **Demo**: http://localhost:3001/demo
   - **API Docs**: http://localhost:3001/docs
   - **Admin Panel**: Open `admin/index.html` in browser

## Project Structure

```
adaptive-storytelling-agent/
├── app/
│   ├── core/           # Core business logic
│   ├── services/       # AWS service integrations
│   ├── api/           # FastAPI endpoints
│   ├── models/        # Data models
│   └── utils/         # Utilities and helpers
├── demo/              # Demo web interface
├── tests/             # Test suite
└── docs/              # Documentation
```

## Architecture

The system uses a modular architecture with:
- **FastAPI** for the web service
- **AWS Bedrock** for story generation
- **AWS Transcribe** for voice emotion detection
- **AWS Rekognition** for visual emotion detection
- **AWS Polly** for text-to-speech narration

## Development

See the [Implementation Plan](.kiro/specs/adaptive-storytelling-agent/tasks.md) for detailed development tasks.