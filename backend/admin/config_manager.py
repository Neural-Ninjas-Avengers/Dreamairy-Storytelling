#!/usr/bin/env python3
"""
Configuration Manager for DreamAIry Admin Module
Handles secure storage and retrieval of AWS credentials and configuration
"""

import os
import json
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Secure configuration management for AWS credentials and settings"""
    
    def __init__(self, config_dir="backend/admin/config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "admin_config.json")
        self.key_file = os.path.join(config_dir, "admin.key")
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
        
        # Default configuration
        self.default_config = {
            "environment": "demo",
            "aws": {
                "enabled": False,
                "credentials": None,
                "region": "eu-west-1",
                "services": {
                    "bedrock": {
                        "enabled": False,
                        "modelId": "amazon.titan-text-express-v1",
                        "maxTokens": 1000,
                        "temperature": 0.7
                    },
                    "polly": {
                        "enabled": False,
                        "voiceId": "Joanna",
                        "engine": "neural",
                        "languageCode": "en-US"
                    },
                    "rekognition": {
                        "enabled": False,
                        "confidenceThreshold": 80,
                        "maxFaces": 10
                    },
                    "s3": {
                        "enabled": False,
                        "bucketName": "",
                        "region": "eu-west-1"
                    },
                    "dynamodb": {
                        "enabled": False,
                        "tableName": "DreamAIry-Sessions",
                        "region": "eu-west-1"
                    }
                }
            },
            "fallbacks": {
                "huggingface": {
                    "enabled": True,
                    "apiKey": None
                },
                "pollinations": {
                    "enabled": True,
                    "rateLimit": 10
                }
            },
            "security": {
                "dataRetentionDays": 30,
                "encryptionEnabled": True,
                "auditLogging": True
            },
            "monitoring": {
                "healthChecks": True,
                "costAlerts": True,
                "costLimit": 100.00
            },
            "lastUpdated": None,
            "version": "1.0.0"
        }
    
    def _init_encryption(self):
        """Initialize encryption key for secure credential storage"""
        try:
            if os.path.exists(self.key_file):
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    self.key = f.read()
            else:
                # Generate new key
                self.key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(self.key)
                # Secure the key file
                os.chmod(self.key_file, 0o600)
            
            self.cipher = Fernet(self.key)
            logger.info("Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
            
            encrypted = self.cipher.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            if not encrypted_data:
                return None
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            
            # Try to parse as JSON, otherwise return as string
            try:
                return json.loads(decrypted.decode('utf-8'))
            except json.JSONDecodeError:
                return decrypted.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Decrypt sensitive data
                if config.get('aws', {}).get('credentials'):
                    config['aws']['credentials'] = self.decrypt_data(config['aws']['credentials'])
                
                if config.get('fallbacks', {}).get('huggingface', {}).get('apiKey'):
                    config['fallbacks']['huggingface']['apiKey'] = self.decrypt_data(
                        config['fallbacks']['huggingface']['apiKey']
                    )
                
                logger.info("Configuration loaded successfully")
                return config
            else:
                logger.info("No existing configuration found, using defaults")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file with encryption"""
        try:
            # Create a copy for encryption
            config_to_save = json.loads(json.dumps(config))  # Deep copy
            
            # Encrypt sensitive data
            if config_to_save.get('aws', {}).get('credentials'):
                config_to_save['aws']['credentials'] = self.encrypt_data(
                    config_to_save['aws']['credentials']
                )
            
            if config_to_save.get('fallbacks', {}).get('huggingface', {}).get('apiKey'):
                config_to_save['fallbacks']['huggingface']['apiKey'] = self.encrypt_data(
                    config_to_save['fallbacks']['huggingface']['apiKey']
                )
            
            # Update timestamp
            config_to_save['lastUpdated'] = datetime.now().isoformat()
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            
            # Secure the config file
            os.chmod(self.config_file, 0o600)
            
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def update_aws_credentials(self, access_key_id, secret_access_key, region="eu-west-1"):
        """Update AWS credentials"""
        try:
            config = self.load_config()
            
            credentials = {
                "accessKeyId": access_key_id,
                "secretAccessKey": secret_access_key,
                "region": region
            }
            
            config['aws']['credentials'] = credentials
            config['aws']['region'] = region
            config['aws']['enabled'] = True
            
            if self.save_config(config):
                logger.info("AWS credentials updated successfully")
                return True
            else:
                logger.error("Failed to save AWS credentials")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update AWS credentials: {e}")
            return False
    
    def get_aws_credentials(self):
        """Get decrypted AWS credentials with region"""
        try:
            config = self.load_config()
            aws_config = config.get('aws', {})
            credentials = aws_config.get('credentials')
            region = aws_config.get('region', 'us-east-1')
            
            if credentials:
                # If credentials is already a dict, use it directly
                if isinstance(credentials, dict):
                    cred_data = credentials.copy()
                else:
                    # Parse the credentials JSON
                    import json
                    cred_data = json.loads(credentials)
                
                # Add region to credentials
                cred_data['region'] = region
                return cred_data
            return None
        except Exception as e:
            logger.error(f"Failed to get AWS credentials: {e}")
            return None
    
    def update_environment(self, environment):
        """Update deployment environment"""
        try:
            if environment not in ['demo', 'staging', 'production']:
                raise ValueError("Invalid environment. Must be 'demo', 'staging', or 'production'")
            
            config = self.load_config()
            config['environment'] = environment
            
            # Adjust settings based on environment
            if environment == 'demo':
                config['aws']['enabled'] = False
                config['fallbacks']['pollinations']['enabled'] = True
                config['fallbacks']['huggingface']['enabled'] = True
            elif environment == 'staging':
                config['aws']['enabled'] = True
                # Reduced capacity for staging
                config['aws']['services']['bedrock']['maxTokens'] = 500
            elif environment == 'production':
                config['aws']['enabled'] = True
                # Full capacity for production
                config['aws']['services']['bedrock']['maxTokens'] = 1000
            
            if self.save_config(config):
                logger.info(f"Environment updated to {environment}")
                return True
            else:
                logger.error(f"Failed to save environment update")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update environment: {e}")
            return False
    
    def get_current_environment(self):
        """Get current deployment environment"""
        try:
            config = self.load_config()
            return config.get('environment', 'demo')
        except Exception as e:
            logger.error(f"Failed to get current environment: {e}")
            return 'demo'
    
    def backup_config(self, backup_path=None):
        """Create encrypted backup of configuration"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(self.config_dir, f"backup_{timestamp}.json")
            
            config = self.load_config()
            
            # Create backup with metadata
            backup_data = {
                "backup_timestamp": datetime.now().isoformat(),
                "version": config.get('version', '1.0.0'),
                "config": config
            }
            
            # Encrypt entire backup
            encrypted_backup = self.encrypt_data(backup_data)
            
            with open(backup_path, 'w') as f:
                json.dump({"encrypted_data": encrypted_backup}, f)
            
            logger.info(f"Configuration backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_config(self, backup_path):
        """Restore configuration from encrypted backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_file = json.load(f)
            
            encrypted_data = backup_file.get('encrypted_data')
            if not encrypted_data:
                raise ValueError("Invalid backup file format")
            
            backup_data = self.decrypt_data(encrypted_data)
            if not backup_data:
                raise ValueError("Failed to decrypt backup data")
            
            config = backup_data.get('config')
            if not config:
                raise ValueError("No configuration found in backup")
            
            if self.save_config(config):
                logger.info(f"Configuration restored from {backup_path}")
                return True
            else:
                logger.error("Failed to save restored configuration")
                return False
                
        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")
            return False
    
    def validate_aws_credentials(self, access_key_id, secret_access_key, region):
        """Validate AWS credentials by testing connection"""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Create a test session
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            
            # Test with STS (Security Token Service) - lightweight test
            sts = session.client('sts')
            response = sts.get_caller_identity()
            
            logger.info(f"AWS credentials validated for account: {response.get('Account')}")
            return True, "Credentials validated successfully"
            
        except NoCredentialsError:
            return False, "Invalid credentials provided"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidUserID.NotFound':
                return False, "Access Key ID not found"
            elif error_code == 'SignatureDoesNotMatch':
                return False, "Secret Access Key is incorrect"
            else:
                return False, f"AWS Error: {e.response['Error']['Message']}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"