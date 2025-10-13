#!/usr/bin/env python3
"""
Dynamic Client Selector - Selects AWS or mock clients based on current admin configuration
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

def get_current_bedrock_client():
    """Get the appropriate Bedrock client based on current admin configuration"""
    try:
        from backend.admin.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        if admin_config:
            environment = admin_config.get('environment', 'demo')
            aws_enabled = admin_config.get('aws', {}).get('enabled', False)
            
            # Use AWS if environment is staging/production AND AWS is enabled
            if environment in ['staging', 'production'] and aws_enabled:
                logger.info(f"Using AWS Bedrock client for {environment} environment")
                from backend.services.aws_clients import BedrockClient
                return BedrockClient()
            else:
                logger.info(f"Using mock Bedrock client for {environment} environment")
                from backend.services.mock_services import MockBedrockClient
                return MockBedrockClient()
        else:
            # Fallback to mock if no admin config
            logger.info("No admin config found, using mock Bedrock client")
            from backend.services.mock_services import MockBedrockClient
            return MockBedrockClient()
            
    except Exception as e:
        logger.error(f"Error selecting Bedrock client: {e}")
        # Fallback to mock on error
        from backend.services.mock_services import MockBedrockClient
        return MockBedrockClient()

def get_current_image_generator():
    """Get the appropriate image generator based on current admin configuration"""
    try:
        from backend.admin.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        if admin_config:
            environment = admin_config.get('environment', 'demo')
            aws_enabled = admin_config.get('aws', {}).get('enabled', False)
            
            # Use AWS if environment is staging/production AND AWS is enabled
            if environment in ['staging', 'production'] and aws_enabled:
                logger.info(f"Using AWS image generation for {environment} environment")
                return "aws"
            else:
                logger.info(f"Using free image generation for {environment} environment")
                return "free"
        else:
            logger.info("No admin config found, using free image generation")
            return "free"
            
    except Exception as e:
        logger.error(f"Error selecting image generator: {e}")
        return "free"

def should_use_aws_services() -> bool:
    """Check if AWS services should be used based on current admin configuration"""
    try:
        from backend.admin.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        admin_config = config_manager.load_config()
        
        if admin_config:
            environment = admin_config.get('environment', 'demo')
            aws_enabled = admin_config.get('aws', {}).get('enabled', False)
            
            return environment in ['staging', 'production'] and aws_enabled
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking AWS services status: {e}")
        return False