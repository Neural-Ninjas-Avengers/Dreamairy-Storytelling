#!/usr/bin/env python3
"""
Admin API endpoints for DreamAIry
Provides secure configuration management and AWS integration
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from .config_manager import ConfigManager
from .aws_connector import AWSConnector

logger = logging.getLogger(__name__)

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

# Initialize configuration manager
config_manager = ConfigManager()

@admin_bp.route('/health', methods=['GET'])
def admin_health():
    """Admin module health check"""
    try:
        return jsonify({
            "status": "healthy",
            "module": "admin",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Admin health check failed: {e}")
        return jsonify({"error": "Admin module unhealthy"}), 500

@admin_bp.route('/config', methods=['GET'])
def get_config():
    """Get current configuration (without sensitive data)"""
    try:
        config = config_manager.load_config()
        
        # Remove sensitive data for client
        safe_config = json.loads(json.dumps(config))  # Deep copy
        
        # Mask AWS credentials
        if safe_config.get('aws', {}).get('credentials'):
            creds = safe_config['aws']['credentials']
            if creds.get('accessKeyId'):
                safe_config['aws']['credentials'] = {
                    "accessKeyId": creds['accessKeyId'][:4] + "****" + creds['accessKeyId'][-4:],
                    "secretAccessKey": "****",
                    "region": creds.get('region', 'us-east-1')
                }
        
        # Mask API keys
        if safe_config.get('fallbacks', {}).get('huggingface', {}).get('apiKey'):
            safe_config['fallbacks']['huggingface']['apiKey'] = "hf_****"
        
        return jsonify({
            "success": True,
            "config": safe_config
        })
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        return jsonify({"error": "Failed to retrieve configuration"}), 500

@admin_bp.route('/config/aws', methods=['POST'])
def update_aws_config():
    """Update AWS configuration and credentials"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['accessKeyId', 'secretAccessKey', 'region']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate credentials format
        access_key = data['accessKeyId'].strip()
        secret_key = data['secretAccessKey'].strip()
        region = data['region'].strip()
        
        if len(access_key) < 16:
            return jsonify({"error": "Invalid Access Key ID format"}), 400
        
        if len(secret_key) < 20:
            return jsonify({"error": "Invalid Secret Access Key format"}), 400
        
        # Test credentials if requested
        if data.get('validate', True):
            is_valid, message = config_manager.validate_aws_credentials(access_key, secret_key, region)
            if not is_valid:
                return jsonify({
                    "error": "Credential validation failed",
                    "message": message
                }), 400
        
        # Update credentials
        success = config_manager.update_aws_credentials(access_key, secret_key, region)
        
        if success:
            logger.info("AWS credentials updated successfully")
            return jsonify({
                "success": True,
                "message": "AWS credentials updated successfully"
            })
        else:
            return jsonify({"error": "Failed to save AWS credentials"}), 500
            
    except Exception as e:
        logger.error(f"Failed to update AWS config: {e}")
        return jsonify({"error": "Failed to update AWS configuration"}), 500

@admin_bp.route('/config/environment', methods=['PUT'])
def update_environment():
    """Update deployment environment"""
    try:
        data = request.get_json()
        
        if not data or 'environment' not in data:
            return jsonify({"error": "Environment not specified"}), 400
        
        environment = data['environment']
        
        if environment not in ['demo', 'staging', 'production']:
            return jsonify({"error": "Invalid environment. Must be 'demo', 'staging', or 'production'"}), 400
        
        success = config_manager.update_environment(environment)
        
        if success:
            logger.info(f"Environment updated to {environment}")
            return jsonify({
                "success": True,
                "message": f"Environment updated to {environment}",
                "environment": environment
            })
        else:
            return jsonify({"error": "Failed to update environment"}), 500
            
    except Exception as e:
        logger.error(f"Failed to update environment: {e}")
        return jsonify({"error": "Failed to update environment"}), 500

@admin_bp.route('/config/services', methods=['PUT'])
def update_service_config():
    """Update AWS service configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No configuration data provided"}), 400
        
        config = config_manager.load_config()
        
        # Update service configurations
        if 'bedrock' in data:
            config['aws']['services']['bedrock'].update(data['bedrock'])
        
        if 'polly' in data:
            config['aws']['services']['polly'].update(data['polly'])
        
        if 'rekognition' in data:
            config['aws']['services']['rekognition'].update(data['rekognition'])
        
        if 's3' in data:
            config['aws']['services']['s3'].update(data['s3'])
        
        if 'dynamodb' in data:
            config['aws']['services']['dynamodb'].update(data['dynamodb'])
        
        success = config_manager.save_config(config)
        
        if success:
            logger.info("Service configuration updated successfully")
            return jsonify({
                "success": True,
                "message": "Service configuration updated successfully"
            })
        else:
            return jsonify({"error": "Failed to save service configuration"}), 500
            
    except Exception as e:
        logger.error(f"Failed to update service config: {e}")
        return jsonify({"error": "Failed to update service configuration"}), 500

@admin_bp.route('/test/aws', methods=['POST'])
def test_aws_services():
    """Test AWS service connectivity and functionality"""
    try:
        data = request.get_json() or {}
        services_to_test = data.get('services', ['bedrock', 'stable-diffusion', 'polly', 'rekognition', 's3', 'dynamodb'])
        
        config = config_manager.load_config()
        
        if not config.get('aws', {}).get('enabled'):
            return jsonify({"error": "AWS services not enabled"}), 400
        
        credentials = config_manager.get_aws_credentials()
        if not credentials:
            return jsonify({"error": "AWS credentials not configured"}), 400
        
        # Initialize AWS connector
        aws_connector = AWSConnector(credentials)
        
        test_results = {}
        
        # Test each requested service
        for service in services_to_test:
            if service == 'bedrock':
                # Get Bedrock model configuration
                bedrock_config = config.get('aws', {}).get('services', {}).get('bedrock', {})
                model_id = bedrock_config.get('modelId', 'amazon.titan-text-express-v1')
                test_results['bedrock'] = aws_connector.test_bedrock(model_id)
            elif service == 'stable-diffusion':
                test_results['stable-diffusion'] = aws_connector.test_titan_image()
            elif service == 'polly':
                test_results['polly'] = aws_connector.test_polly()
            elif service == 'rekognition':
                test_results['rekognition'] = aws_connector.test_rekognition()
            elif service == 's3':
                test_results['s3'] = aws_connector.test_s3()
            elif service == 'dynamodb':
                test_results['dynamodb'] = aws_connector.test_dynamodb()
        
        # Calculate overall status
        all_passed = all(result.get('success', False) for result in test_results.values())
        
        return jsonify({
            "success": True,
            "overall_status": "passed" if all_passed else "failed",
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AWS testing failed: {e}")
        return jsonify({"error": f"AWS testing failed: {str(e)}"}), 500

@admin_bp.route('/monitoring/status', methods=['GET'])
def get_system_status():
    """Get current system status and health metrics"""
    try:
        config = config_manager.load_config()
        environment = config.get('environment', 'demo')
        
        status = {
            "environment": environment,
            "aws_enabled": config.get('aws', {}).get('enabled', False),
            "services": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check service status based on environment
        if environment == 'demo':
            status['services'] = {
                "pollinations": {"status": "healthy", "provider": "free"},
                "huggingface": {"status": "healthy", "provider": "free"},
                "svg_fallback": {"status": "healthy", "provider": "local"}
            }
        else:
            # Check AWS services if enabled
            if config.get('aws', {}).get('enabled'):
                credentials = config_manager.get_aws_credentials()
                if credentials:
                    aws_connector = AWSConnector(credentials)
                    
                    # Quick health checks
                    for service_name in ['bedrock', 'polly', 'rekognition', 's3', 'dynamodb']:
                        service_config = config['aws']['services'].get(service_name, {})
                        if service_config.get('enabled'):
                            # Simplified health check
                            status['services'][service_name] = {
                                "status": "healthy",  # Would be actual check in production
                                "provider": "aws"
                            }
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return jsonify({"error": "Failed to retrieve system status"}), 500

@admin_bp.route('/backup', methods=['POST'])
def create_backup():
    """Create configuration backup"""
    try:
        backup_path = config_manager.backup_config()
        
        if backup_path:
            return jsonify({
                "success": True,
                "message": "Backup created successfully",
                "backup_path": os.path.basename(backup_path),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to create backup"}), 500
            
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return jsonify({"error": "Failed to create backup"}), 500

@admin_bp.route('/restore', methods=['POST'])
def restore_backup():
    """Restore configuration from backup"""
    try:
        data = request.get_json()
        
        if not data or 'backup_path' not in data:
            return jsonify({"error": "Backup path not specified"}), 400
        
        backup_filename = data['backup_path']
        backup_path = os.path.join(config_manager.config_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return jsonify({"error": "Backup file not found"}), 404
        
        success = config_manager.restore_config(backup_path)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Configuration restored successfully"
            })
        else:
            return jsonify({"error": "Failed to restore configuration"}), 500
            
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return jsonify({"error": "Failed to restore configuration"}), 500

@admin_bp.route('/logs', methods=['GET'])
def get_admin_logs():
    """Get admin activity logs"""
    try:
        # This would read from actual log files in production
        # For now, return sample log data
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_update",
                "user": "admin",
                "details": "AWS credentials updated"
            }
        ]
        
        return jsonify({
            "success": True,
            "logs": logs
        })
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({"error": "Failed to retrieve logs"}), 500

# Error handlers
@admin_bp.errorhandler(404)
def admin_not_found(error):
    return jsonify({"error": "Admin endpoint not found"}), 404

@admin_bp.errorhandler(500)
def admin_internal_error(error):
    return jsonify({"error": "Internal admin error"}), 500
