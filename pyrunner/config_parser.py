"""
Configuration file parser for ONE Simulator .cfg files.

Parses .cfg files, extracts key-value pairs, and filters highlighted settings.
"""

from typing import Dict


def parse_config_file(cfg_file_path: str) -> Dict[str, str]:
    """
    Parse a .cfg configuration file and extract all key-value pairs.
    
    Reads the config file line by line and extracts settings of the form:
    key = value
    
    Lines starting with '#' (comments) or '[' (section headers) are skipped.
    Trailing whitespace is stripped from values.
    """
    config_dict = {}
    
    try:
        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip leading/trailing whitespace from the line
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Skip comment lines (starting with #)
                if line.startswith('#'):
                    continue
                
                # Skip section headers (lines enclosed in [ ])
                if line.startswith('['):
                    continue
                
                # Parse key = value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove inline comments (anything after # in the value)
                    if '#' in value:
                        value = value.split('#', 1)[0].strip()
                    
                    # Skip lines with empty keys or values
                    if key and value:
                        config_dict[key] = value
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {cfg_file_path}")
    except IOError as e:
        raise IOError(f"Error reading config file {cfg_file_path}: {e}")
    
    return config_dict


def extract_highlighted_settings(
        config_dict: Dict[str, str],
        highlighted_keys: list
) -> Dict[str, str]:
    """
    Extract only the settings that are in the highlighted_keys list.
    """
    highlighted_settings = {}
    
    for key in highlighted_keys:
        if key in config_dict:
            highlighted_settings[key] = config_dict[key]
    
    return highlighted_settings

