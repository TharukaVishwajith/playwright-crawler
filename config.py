"""
Configuration settings for the e-commerce analytics automation project.
"""

import os
from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Browser configuration
BROWSER_CONFIG = {
    "headless": False,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# URLs
BASE_URL = "https://www.bestbuy.com"
LAPTOPS_URL = f"{BASE_URL}/site/shop/laptop-computers"

# Wait timeouts (in milliseconds)
DEFAULT_TIMEOUT = 60000
NAVIGATION_TIMEOUT = 90000
ELEMENT_WAIT_TIMEOUT = 20000

# Rate limiting
REQUEST_DELAY = 1  # seconds between requests
PAGE_LOAD_DELAY = 2  # seconds to wait after page load

# Filter settings
PRICE_RANGE = {
    "min": 500,
    "max": 1500
}

RATING_THRESHOLD = 4.0

TOP_BRANDS = ["Apple", "Dell", "HP"]

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": LOGS_DIR / "automation.log"
} 