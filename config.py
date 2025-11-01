"""
Configuration file for Crime Report Extractor
Store your API keys and settings here
"""

import os
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your-api-key-here')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'

# Processing Settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
TEMPERATURE = 0.1  # Low temperature for consistent extraction
REQUEST_TIMEOUT = 30  # seconds

# Input/Output Paths
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
DEFAULT_INPUT_FILE = 'crime_data.xlsx'
DEFAULT_OUTPUT_FILE = 'crime_data_extracted.xlsx'
CRIME_CODES_FILE = 'crime_codes.csv'

# Column Names (customize based on your input file)
INPUT_COLUMNS = {
    'crime_code': 'crime_code',  # Column name for crime code
    'narrative': 'narrative'      # Column name for narrative text
}

# Output Columns
OUTPUT_COLUMNS = [
    'crime_code',
    'narrative',
    'crime_type',
    'method_of_entry',
    'suspect_1',
    'suspect_2',
    'vehicle_make',
    'vehicle_model',
    'vehicle_color',
    'vehicle_plate'
]
