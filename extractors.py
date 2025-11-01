"""
Extraction functions for crime report data
Includes both regex-based and LLM-based extraction methods
"""

import re
import json
import time
import requests
from typing import Dict, List, Optional
import config


# ============================================================================
# REGEX-BASED EXTRACTION (Fallback and Fast Operations)
# ============================================================================

def extract_entry_method_regex(narrative: str) -> str:
    """
    Extract method of entry using regex patterns
    Returns the first matching method or 'Not specified'
    """
    entry_methods = {
        'window_smash': r'(broke|smashed|shattered|broken).{0,15}(window|glass)',
        'door_pry': r'(pried|forced|jimmied|pry).{0,15}(door|entry)',
        'door_kick': r'(kicked|boot|kick).{0,15}door',
        'lock_pick': r'(picked|pick).{0,15}lock',
        'unlocked': r'(unlocked|open|unsecured).{0,15}(door|window|entry)',
        'cut_screen': r'(cut|sliced).{0,15}(screen|mesh)',
        'garage_door': r'(garage|overhead).{0,15}door',
        'unknown': r'(unknown|undetermined).{0,15}(entry|method|access)'
    }

    narrative_lower = narrative.lower()

    for method, pattern in entry_methods.items():
        if re.search(pattern, narrative_lower):
            return method.replace('_', ' ')

    return 'Not specified'


def extract_license_plate_regex(narrative: str) -> Optional[str]:
    """
    Extract license plate using common patterns
    Supports formats like: ABC123, 1ABC234, AB-1234, etc.
    """
    # Common license plate patterns
    patterns = [
        r'\b[A-Z]{2,3}[-\s]?[0-9]{3,4}\b',  # ABC123, AB-1234
        r'\b[0-9][A-Z]{2,3}[-\s]?[0-9]{3}\b',  # 1ABC234
        r'\b[A-Z]{3}[-\s]?[0-9]{4}\b',  # ABC-1234
    ]

    for pattern in patterns:
        match = re.search(pattern, narrative.upper())
        if match:
            return match.group(0).replace(' ', '').replace('-', '')

    return None


def extract_vehicle_regex(narrative: str) -> Dict[str, Optional[str]]:
    """
    Extract basic vehicle information using regex
    Returns dict with make, model, color, plate
    """
    result = {
        'make': None,
        'model': None,
        'color': None,
        'plate': None
    }

    # Common car makes
    makes = [
        'honda', 'toyota', 'ford', 'chevrolet', 'chevy', 'nissan',
        'bmw', 'mercedes', 'tesla', 'hyundai', 'kia', 'mazda',
        'dodge', 'jeep', 'ram', 'gmc', 'volkswagen', 'vw', 'audi',
        'lexus', 'acura', 'infiniti', 'subaru', 'volvo'
    ]

    # Common colors
    colors = [
        'black', 'white', 'red', 'blue', 'silver', 'grey', 'gray',
        'green', 'yellow', 'orange', 'brown', 'tan', 'beige',
        'gold', 'maroon', 'purple'
    ]

    narrative_lower = narrative.lower()

    # Extract make
    for make in makes:
        if re.search(r'\b' + make + r'\b', narrative_lower):
            result['make'] = make.title()
            break

    # Extract color
    for color in colors:
        if re.search(r'\b' + color + r'\b', narrative_lower):
            result['color'] = color.title()
            break

    # Extract plate
    result['plate'] = extract_license_plate_regex(narrative)

    return result


def fallback_regex_extraction(narrative: str) -> Dict:
    """
    Complete fallback extraction using only regex
    Used when LLM API is unavailable
    """
    vehicle = extract_vehicle_regex(narrative)

    return {
        'method_of_entry': extract_entry_method_regex(narrative),
        'suspects': [],  # Regex not reliable for suspect extraction
        'vehicles': [vehicle] if any(vehicle.values()) else []
    }


# ============================================================================
# LLM-BASED EXTRACTION (Primary Method - Higher Accuracy)
# ============================================================================

def extract_with_llm(narrative: str, crime_code: str) -> Dict:
    """
    Extract structured information using DeepSeek LLM
    Returns dict with method_of_entry, suspects, and vehicles
    """
    prompt = f"""You are extracting structured information from a police crime report narrative.

Crime Code: {crime_code}
Narrative: {narrative}

Extract the following information and return ONLY valid JSON (no markdown, no explanation):

{{
  "method_of_entry": "string (e.g., 'window smash', 'door pry', 'unlocked', 'unknown')",
  "suspects": [
    {{"id": "S1", "description": "brief physical description"}},
    {{"id": "S2", "description": "brief physical description"}}
  ],
  "vehicles": [
    {{"make": "string or null", "model": "string or null", "color": "string or null", "plate": "string or null"}}
  ]
}}

Rules:
- If information is not mentioned, use null
- Keep descriptions brief (under 20 words)
- Only include suspects explicitly mentioned (look for S1, S2, Subject 1, Subject 2, Suspect 1, etc.)
- Extract vehicle details even if partial (e.g., just color and make)
- For method_of_entry, choose from: window smash, door pry, door kick, unlocked, cut screen, garage door, unknown, or describe briefly
- Return ONLY the JSON object, no markdown formatting"""

    try:
        response = requests.post(
            config.DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {config.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': config.DEEPSEEK_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': config.TEMPERATURE
            },
            timeout=config.REQUEST_TIMEOUT
        )

        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content']

        # Clean potential markdown formatting
        result = result.strip()
        result = re.sub(r'^```json\s*', '', result)
        result = re.sub(r'^```\s*', '', result)
        result = re.sub(r'\s*```$', '', result)

        # Parse JSON
        extracted_data = json.loads(result)

        # Validate structure
        if not isinstance(extracted_data, dict):
            raise ValueError("LLM did not return a valid JSON object")

        # Ensure required keys exist
        if 'method_of_entry' not in extracted_data:
            extracted_data['method_of_entry'] = None
        if 'suspects' not in extracted_data:
            extracted_data['suspects'] = []
        if 'vehicles' not in extracted_data:
            extracted_data['vehicles'] = []

        return extracted_data

    except Exception as e:
        raise Exception(f"LLM extraction failed: {str(e)}")


def extract_with_llm_safe(narrative: str, crime_code: str, retries: int = None) -> Dict:
    """
    Wrapper for LLM extraction with retry logic and fallback
    Returns extracted data or falls back to regex extraction
    """
    if retries is None:
        retries = config.MAX_RETRIES

    last_error = None

    for attempt in range(retries):
        try:
            return extract_with_llm(narrative, crime_code)
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(config.RETRY_DELAY)
            continue

    # If all retries failed, fallback to regex
    print(f"⚠️  LLM extraction failed after {retries} attempts: {last_error}")
    print("   Falling back to regex extraction...")
    return fallback_regex_extraction(narrative)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_suspect_description(description: str) -> str:
    """Clean and format suspect description"""
    if not description or description == 'null':
        return None
    return description.strip()[:100]  # Limit to 100 chars


def format_license_plate(plate: str) -> str:
    """Standardize license plate format"""
    if not plate or plate == 'null':
        return None
    return plate.upper().replace(' ', '').replace('-', '')
