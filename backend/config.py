"""Configuration management for the Adaptive Storytelling Agent."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with AWS configuration validation."""
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = Field(default=None, env="AWS_SESSION_TOKEN")
    
    # AWS Service Configuration
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0", 
        env="BEDROCK_MODEL_ID"
    )
    polly_voice_id: str = Field(default="Joanna", env="POLLY_VOICE_ID")
    s3_bucket_name: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    
    # Application Configuration
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://localhost:8080,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:8000", 
        env="CORS_ORIGINS"
    )
    
    # Demo Configuration - IMPORTANTE PARA EVITAR COSTOS
    demo_mode: bool = Field(default=True, env="DEMO_MODE")
    offline_mode: bool = Field(default=True, env="OFFLINE_MODE")  # NUEVO: Modo sin AWS
    use_mock_services: bool = Field(default=True, env="USE_MOCK_SERVICES")  # NUEVO: Servicios simulados
    max_session_duration: int = Field(default=1800, env="MAX_SESSION_DURATION")  # 30 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate_aws_config(self) -> bool:
        """Validate that required AWS configuration is present."""
        # En modo offline, no necesitamos AWS
        if self.offline_mode or self.use_mock_services:
            return True
            
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            return False
        return True
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def is_aws_enabled(self) -> bool:
        """Check if AWS services should be used."""
        # Check admin configuration first
        try:
            from backend.admin.config_manager import ConfigManager
            admin_config_manager = ConfigManager()
            admin_config = admin_config_manager.load_config()
            
            # If admin config exists, use it to determine AWS usage
            if admin_config:
                environment = admin_config.get('environment', 'demo')
                aws_enabled = admin_config.get('aws', {}).get('enabled', False)
                
                # Only use AWS if environment is staging/production AND AWS is enabled
                if environment in ['staging', 'production'] and aws_enabled:
                    return self.validate_aws_config()
                else:
                    return False
            
        except Exception as e:
            # Fallback to original logic if admin config fails
            pass
        
        # Original logic as fallback
        return not self.offline_mode and not self.use_mock_services and self.validate_aws_config()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings