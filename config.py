#!/usr/bin/env python
"""
Configuration loader for the contact scraper
Loads settings from .env file or environment variables
"""

import os
from pathlib import Path


def load_config():
    """
    Load configuration from .env file if it exists.
    Falls back to environment variables.
    """
    # Try to load from .env file
    env_file = Path(__file__).parent / '.env'
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()


# Load config on import
load_config()


# Configuration values
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
AI_MODEL = os.environ.get('AI_MODEL', 'openai/gpt-4o-mini')
USE_AI_EXTRACTION = os.environ.get('USE_AI_EXTRACTION', 'true').lower() in ('true', '1', 'yes')


def get_config():
    """Get current configuration as dict."""
    return {
        'openrouter_api_key': OPENROUTER_API_KEY,
        'ai_model': AI_MODEL,
        'use_ai_extraction': USE_AI_EXTRACTION,
        'ai_enabled': bool(OPENROUTER_API_KEY) and USE_AI_EXTRACTION
    }


if __name__ == "__main__":
    config = get_config()
    print("Current Configuration:")
    print(f"  AI Extraction: {'✓ Enabled' if config['ai_enabled'] else '✗ Disabled'}")
    print(f"  AI Model: {config['ai_model']}")
    print(f"  API Key: {'Set' if config['openrouter_api_key'] else 'Not Set'}")

