# AWS Services Architecture - DreamAIry

## Diagrama de Arquitectura

```mermaid
graph TB
    subgraph "Frontend - React App"
        UI[User Interface]
        SS[StorytellingService]
        CDS[ClaudeDesignService]
    end

    subgraph "Backend - Flask API"
        API[Flask API Endpoints]
        AWC[AWSConnector]
        AIS[AIImageService]
        SG[StoryGenerator]
    end

    subgraph "AWS Services"
        subgraph "Amazon Bedrock"
            TITAN_TEXT[Titan Text G1<br/>Story Generation]
            TITAN_IMG[Titan Image G1<br/>Image Generation]
            CLAUDE[Claude 3.5 Sonnet<br/>Design Analysis]
        end
        
        subgraph "Amazon Polly"
            POLLY[Text-to-Speech<br/>Voice: Lucia/Joanna]
        end
        
        subgraph "Amazon Rekognition"
            REKOG[Image Analysis<br/>Content Moderation]
        end
    end

    subgraph "Configuration"
        CONFIG[admin_config.json<br/>Credentials & Settings]
    end

    %% User Flow
    UI -->|1. User Actions| SS
    UI -->|Design Requests| CDS
    
    %% Story Generation Flow
    SS -->|2. Generate Story| API
    API -->|3. Load Config| CONFIG
    API -->|4. Story Request| AWC
    AWC -->|5. Invoke Model| TITAN_TEXT
    TITAN_TEXT -->|6. Story Text| AWC
    AWC -->|7. Response| API
    API -->|8. Story JSON| SS
    SS -->|9. Display| UI

    %% Image Generation Flow
    SS -->|10. Generate Image| API
    API -->|11. Image Request| AIS
    AIS -->|12. Check Photo| REKOG
    REKOG -->|13. Moderation Result| AIS
    AIS -->|14. Generate| TITAN_IMG
    TITAN_IMG -->|15. Image Base64| AIS
    AIS -->|16. Response| API
    API -->|17. Image Data| SS
    SS -->|18. Display| UI

    %% Text-to-Speech Flow
    SS -->|19. TTS Request| API
    API -->|20. Synthesize| POLLY
    POLLY -->|21. Audio Stream| API
    API -->|22. Audio Data| SS
    SS -->|23. Play Audio| UI

    %% Design Analysis Flow
    CDS -->|24. Design Analysis| API
    API -->|25. Analyze| CLAUDE
    CLAUDE -->|26. Design Feedback| API
    API -->|27. Suggestions| CDS
    CDS -->|28. Apply| UI

    style TITAN_TEXT fill:#FF9900
    style TITAN_IMG fill:#FF9900
    style CLAUDE fill:#FF9900
    style POLLY fill:#FF9900
    style REKOG fill:#FF9900
    style CONFIG fill:#4CAF50
```

## Flujo Detallado por Servicio

### 1. 📚 Story Generation (Amazon Bedrock - Titan Text)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Bedrock
    
    User->>Frontend: Click "Start Story"
    Frontend->>Backend: POST /api/v1/demo/sessions/{id}/story
    Note over Backend: Load credentials from config
    Backend->>Bedrock: invoke_model(titan-text-express-v1)
    Note over Bedrock: Generate story with prompt<br/>Language: EN/ES<br/>Max tokens: 800
    Bedrock-->>Backend: Story text response
    Backend-->>Frontend: JSON with story text
    Frontend-->>User: Display story chapter
```

**Endpoint**: `/api/v1/demo/sessions/{session_id}/story`  
**Model**: `amazon.titan-text-express-v1`  
**Input**: Story prompt with context, theme, age, language  
**Output**: Story text (4-6 sentences)  
**Cost**: ~$0.0002 per request

---

### 2. 🎨 Image Generation (Amazon Bedrock - Titan Image)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Rekognition
    participant Bedrock
    
    User->>Frontend: Story segment displayed
    Frontend->>Backend: POST /api/v1/demo/sessions/{id}/image
    
    alt User Photo Provided
        Backend->>Rekognition: detect_moderation_labels()
        Rekognition-->>Backend: Safety check result
    end
    
    Backend->>Bedrock: invoke_model(titan-image-generator-v1)
    Note over Bedrock: Generate illustration<br/>Style: Children's book<br/>Include user character
    Bedrock-->>Backend: Image base64
    Backend-->>Frontend: JSON with image data
    Frontend-->>User: Display illustration
```

**Endpoint**: `/api/v1/demo/sessions/{session_id}/image`  
**Model**: `amazon.titan-image-generator-v1`  
**Input**: Scene description, theme, user photo (optional)  
**Output**: Base64 encoded image (1024x1024)  
**Cost**: ~$0.01 per image

---

### 3. 🗣️ Text-to-Speech (Amazon Polly)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Polly
    
    User->>Frontend: Click "Read Story"
    Frontend->>Backend: POST /api/v1/demo/sessions/{id}/tts
    Backend->>Polly: synthesize_speech()
    Note over Polly: Voice: Lucia (ES)<br/>or Joanna (EN)<br/>Engine: Neural
    Polly-->>Backend: Audio stream (MP3)
    Backend-->>Frontend: Audio data
    Frontend-->>User: Play audio
```

**Endpoint**: `/api/v1/demo/sessions/{session_id}/tts`  
**Voices**: 
- Spanish: Lucia (Neural)
- English: Joanna (Neural)
**Output**: MP3 audio stream  
**Cost**: ~$0.000004 per character

---

### 4. 🎭 Design Analysis (Amazon Bedrock - Claude)

```mermaid
sequenceDiagram
    participant Designer
    participant Admin
    participant Backend
    participant Claude
    
    Designer->>Admin: Upload design screenshot
    Admin->>Backend: POST /api/v1/claude-design/analyze
    Backend->>Claude: invoke_model(claude-3-5-sonnet)
    Note over Claude: Analyze UI/UX<br/>Accessibility<br/>Best practices
    Claude-->>Backend: Design feedback
    Backend-->>Admin: Suggestions & improvements
    Admin-->>Designer: Display analysis
```

**Endpoint**: `/api/v1/claude-design/analyze`  
**Model**: `anthropic.claude-3-5-sonnet-20240620-v1:0`  
**Input**: Design screenshot (base64)  
**Output**: Detailed design analysis and suggestions  
**Cost**: ~$0.003 per request

---

### 5. 🔍 Content Moderation (Amazon Rekognition)

```mermaid
sequenceDiagram
    participant User
    participant Backend
    participant Rekognition
    
    User->>Backend: Upload photo
    Backend->>Rekognition: detect_moderation_labels()
    Note over Rekognition: Check for:<br/>- Inappropriate content<br/>- Violence<br/>- Adult content
    
    alt Content Safe
        Rekognition-->>Backend: Safe (confidence < 60%)
        Backend-->>User: Photo accepted
    else Content Unsafe
        Rekognition-->>Backend: Unsafe (confidence > 60%)
        Backend-->>User: Photo rejected
    end
```

**Endpoint**: Used internally in photo upload  
**Service**: `detect_moderation_labels()`  
**Threshold**: 60% confidence  
**Cost**: ~$0.001 per image

---

## Configuration Structure

```json
{
  "aws": {
    "region": "us-east-1",
    "credentials": {
      "access_key_id": "AKIA...",
      "secret_access_key": "...",
      "session_token": "..."
    }
  },
  "services": {
    "bedrock": {
      "models": {
        "text": "amazon.titan-text-express-v1",
        "image": "amazon.titan-image-generator-v1",
        "claude": "anthropic.claude-3-5-sonnet-20240620-v1:0"
      }
    },
    "polly": {
      "voices": {
        "es": "Lucia",
        "en": "Joanna"
      }
    }
  }
}
```

**Note**: AWS services are always enabled in production. No environment flags needed.

## Cost Estimation (per user session)

| Service | Usage | Cost per Request | Typical Session |
|---------|-------|------------------|-----------------|
| **Titan Text** | 5 story chapters | $0.0002 | $0.001 |
| **Titan Image** | 5 illustrations | $0.01 | $0.05 |
| **Polly TTS** | 500 characters | $0.000004/char | $0.002 |
| **Rekognition** | 1 photo check | $0.001 | $0.001 |
| **Claude Design** | Admin only | $0.003 | N/A |
| **Total per session** | | | **~$0.054** |

## Production Configuration

The application runs in **production mode only** with AWS services always enabled:
- AWS services: **Always Enabled**
- Uses: Real AWS services with monitoring
- Cost: **~$0.054 per session**
- All features: Story generation, image generation, TTS, content moderation

## Security & Best Practices

### ✅ Implemented
- Credentials stored in `admin_config.json` (not in code)
- Content moderation for user photos
- Session-based isolation
- Error handling with fallbacks

### 🔒 Recommendations
- Use AWS IAM roles instead of access keys
- Implement AWS Secrets Manager for credentials
- Add CloudWatch monitoring
- Set up billing alerts
- Use AWS WAF for API protection

## Monitoring & Logging

```python
# Current logging format
logger.info("📚 Using REAL AWS Bedrock for story generation")
logger.info("🎨 Using AWS Bedrock Titan for image generation")
logger.info("🗣️ Using REAL AWS Polly for text-to-speech")
logger.info("🌍 Language received from frontend: {language}")
```

### Recommended CloudWatch Metrics
- Bedrock invocation count
- Bedrock latency
- Polly character count
- Rekognition moderation results
- Error rates per service

## Error Handling Strategy

```mermaid
graph LR
    A[AWS Service Call] --> B{Success?}
    B -->|Yes| C[Return AWS Result]
    B -->|No| D[Log Error]
    D --> E[Retry with Exponential Backoff]
    E --> F{Retry Success?}
    F -->|Yes| C
    F -->|No| G[Return Error to User]
```

### Error Handling
- **Story Generation**: Retry up to 3 times, then return error
- **Image Generation**: Retry up to 2 times, then return error
- **Text-to-Speech**: Retry up to 2 times, then return error
- **Content Moderation**: Single attempt, fail-safe to reject on error

## Files Reference

| File | Purpose |
|------|---------|
| `backend/admin/aws_connector.py` | AWS service wrapper |
| `backend/admin/config/admin_config.json` | AWS credentials |
| `backend/app.py` | API endpoints |
| `backend/prompts/story_prompts.py` | Story generation prompts |
| `backend/services/ai_image_service.py` | Image generation logic |
| `backend/api/claude_design.py` | Design analysis API |

## Next Steps

1. **Implement IAM Roles** for better security
2. **Add CloudWatch Dashboards** for monitoring
3. **Set up Cost Alerts** in AWS Billing
4. **Implement Caching** for repeated requests
5. **Add Rate Limiting** to prevent abuse
