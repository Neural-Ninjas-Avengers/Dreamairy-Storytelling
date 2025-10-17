# Claude Design API

API endpoint para integración de Claude 3 Haiku como asistente de diseño.

## Endpoints

### POST `/api/v1/design/claude`

Endpoint principal para solicitudes de diseño a Claude.

**Request Body:**
```json
{
  "model": "anthropic.claude-3-haiku-20240307-v1:0",
  "prompt": "Your design prompt here",
  "max_tokens": 2000,
  "temperature": 0.7,
  "session_id": "optional_session_id"
}
```

**Response (Success):**
```json
{
  "success": true,
  "content": "Claude's response here",
  "model": "anthropic.claude-3-haiku-20240307-v1:0",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message",
  "fallback": true,
  "message": "Claude service unavailable, using fallback"
}
```

**Rate Limiting:**
- 10 requests per minute per session
- Returns 429 status code when exceeded

### GET `/api/v1/design/claude/status`

Verifica el estado del servicio de Claude.

**Response:**
```json
{
  "available": true,
  "model": "anthropic.claude-3-haiku-20240307-v1:0",
  "environment": "production",
  "aws_enabled": true,
  "rate_limit": "10 requests per minute",
  "timestamp": "2024-01-01T12:00:00"
}
```

### POST `/api/v1/design/claude/test`

Prueba la integración de Claude con un prompt simple.

**Response:**
```json
{
  "success": true,
  "test_prompt": "Test prompt",
  "response": "Claude's test response",
  "message": "Claude integration working correctly"
}
```

## Configuración

El endpoint requiere:
1. AWS credentials configuradas en el admin panel
2. Environment set to "staging" o "production"
3. AWS services enabled en la configuración

## Uso desde Frontend

```javascript
// Ejemplo de uso
const response = await fetch('/api/v1/design/claude', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Generate a color palette for a fantasy theme',
    max_tokens: 1000,
    temperature: 0.7,
    session_id: 'my-session-123'
  })
});

const data = await response.json();
if (data.success) {
  console.log('Claude response:', data.content);
} else {
  console.error('Error:', data.error);
}
```

## Rate Limiting

El sistema implementa rate limiting simple en memoria:
- Máximo 10 requests por minuto por session_id
- Las requests antiguas (>60 segundos) se eliminan automáticamente
- Retorna código 429 cuando se excede el límite

## Error Handling

El endpoint maneja los siguientes errores:
- AWS credentials no configuradas
- AWS services no habilitados
- Rate limit excedido
- Errores de red con AWS Bedrock
- Respuestas inválidas de Claude

En caso de error, retorna un response con `success: false` y un mensaje descriptivo.

## Seguridad

- No expone API keys en el frontend
- Todas las llamadas pasan por el backend proxy
- Rate limiting para prevenir abuso
- Validación de parámetros de entrada
- Sanitización de prompts (implementar según necesidad)

## Costos AWS

Cada llamada a Claude 3 Haiku tiene un costo asociado:
- Input: ~$0.00025 por 1K tokens
- Output: ~$0.00125 por 1K tokens

Ejemplo: Un request típico de diseño (~500 tokens input, ~1000 tokens output) cuesta aproximadamente $0.0015 USD.

## Logs

El sistema registra:
- Todas las llamadas a Claude
- Errores y excepciones
- Rate limit violations
- Tamaño de respuestas

Logs disponibles en el logger de Flask con nivel INFO.
