#!/usr/bin/env python3
"""
Claude Design API
Handles Claude 3 Haiku integration for design assistance
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple
from flask import Blueprint, request, jsonify

from admin.config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Create blueprint
claude_design_bp = Blueprint('claude_design', __name__)

# Rate limiting storage (simple in-memory for now)
rate_limit_storage = {}
MAX_REQUESTS_PER_MINUTE = 10


def check_rate_limit(session_id: str) -> bool:
    """Check if request is within rate limit"""
    now = datetime.now().timestamp()
    
    if session_id not in rate_limit_storage:
        rate_limit_storage[session_id] = []
    
    # Remove requests older than 1 minute
    rate_limit_storage[session_id] = [
        timestamp for timestamp in rate_limit_storage[session_id]
        if now - timestamp < 60
    ]
    
    # Check if under limit
    if len(rate_limit_storage[session_id]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add current request
    rate_limit_storage[session_id].append(now)
    return True


def call_claude_haiku(prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Tuple[bool, str, str]:
    """
    Call Claude 3 Haiku via AWS Bedrock
    
    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation (0.0-1.0)
    
    Returns:
        Tuple of (success, response_content, error_message)
    """
    try:
        # Get AWS credentials from config
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        # Check if AWS is enabled
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        
        if environment not in ['staging', 'production'] or not aws_enabled:
            logger.warning("AWS not enabled, returning fallback response")
            return False, "", "AWS services not enabled. Please enable in admin panel."
        
        # Get credentials
        credentials = config_manager.get_aws_credentials()
        if not credentials:
            logger.error("No AWS credentials found")
            return False, "", "AWS credentials not configured"
        
        # Initialize AWS Bedrock client
        import boto3
        
        session = boto3.Session(
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'],
            region_name=credentials.get('region', 'us-east-1')
        )
        
        bedrock_client = session.client('bedrock-runtime')
        
        # Prepare request for Claude 3 Haiku
        # Using Anthropic Messages API format
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        # Call Claude 3 Haiku
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract content from response
        content = response_body.get('content', [])
        if content and len(content) > 0:
            response_text = content[0].get('text', '')
            logger.info(f"Claude Haiku response received: {len(response_text)} characters")
            return True, response_text, ""
        else:
            logger.error("No content in Claude response")
            return False, "", "No content in response"
        
    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        return False, "", str(e)


@claude_design_bp.route('/api/v1/design/claude', methods=['POST'])
def claude_design_request():
    """
    Main endpoint for Claude design requests
    
    Request body:
    {
        "model": "anthropic.claude-3-haiku-20240307-v1:0",
        "prompt": "Your prompt here",
        "max_tokens": 2000,
        "temperature": 0.7,
        "session_id": "optional_session_id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Get optional parameters
        max_tokens = data.get('max_tokens', 2000)
        temperature = data.get('temperature', 0.7)
        session_id = data.get('session_id', 'default')
        
        # Validate parameters
        if max_tokens > 4096:
            max_tokens = 4096
        if temperature < 0 or temperature > 1:
            temperature = 0.7
        
        # Check rate limit
        if not check_rate_limit(session_id):
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Maximum 10 requests per minute"
            }), 429
        
        # Call Claude
        success, response_content, error_message = call_claude_haiku(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if success:
            return jsonify({
                "success": True,
                "content": response_content,
                "model": "anthropic.claude-3-haiku-20240307-v1:0",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Return fallback response
            return jsonify({
                "success": False,
                "error": error_message,
                "fallback": True,
                "message": "Claude service unavailable, using fallback"
            }), 503
        
    except Exception as e:
        logger.error(f"Error in claude_design_request: {e}")
        return jsonify({"error": "Internal server error"}), 500


@claude_design_bp.route('/api/v1/design/claude/status', methods=['GET'])
def claude_status():
    """Check Claude service status"""
    try:
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        environment = admin_config.get('environment', 'demo') if admin_config else 'demo'
        aws_enabled = admin_config.get('aws', {}).get('enabled', False) if admin_config else False
        
        is_available = environment in ['staging', 'production'] and aws_enabled
        
        return jsonify({
            "available": is_available,
            "model": "anthropic.claude-3-haiku-20240307-v1:0",
            "environment": environment,
            "aws_enabled": aws_enabled,
            "rate_limit": f"{MAX_REQUESTS_PER_MINUTE} requests per minute",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking Claude status: {e}")
        return jsonify({"error": "Failed to check status"}), 500


@claude_design_bp.route('/api/v1/design/claude/test', methods=['POST'])
def test_claude():
    """Test Claude integration with a simple prompt"""
    try:
        test_prompt = "Generate a simple color palette for a children's app with a fantasy theme. Return only a JSON object with primary, secondary, and accent colors as hex codes."
        
        success, response_content, error_message = call_claude_haiku(
            prompt=test_prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        if success:
            return jsonify({
                "success": True,
                "test_prompt": test_prompt,
                "response": response_content,
                "message": "Claude integration working correctly"
            })
        else:
            return jsonify({
                "success": False,
                "error": error_message,
                "message": "Claude integration test failed"
            }), 503
        
    except Exception as e:
        logger.error(f"Error testing Claude: {e}")
        return jsonify({"error": "Test failed"}), 500
