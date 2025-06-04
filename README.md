# E-Commerce Analytics Automation

An automated system to analyze product data and customer reviews from Best Buy using Python and Playwright.

## Project Overview

This project implements an automated web scraping and analytics system for e-commerce data collection from Best Buy. It uses Playwright for browser automation with robust error handling and clean code practices.

## Project Structure

```
/project
    /data          # Scraped data and screenshots
    /logs          # Application logs
    /tests         # Unit tests (to be implemented)
    /reports       # Generated reports
    main.py        # Main automation script
    config.py      # Configuration settings
    requirements.txt # Python dependencies
    README.md      # This file
```

## Requirements

- Python 3.11
- Chrome browser (installed automatically by Playwright)

## Installation

1. **Clone or create the project directory:**
   ```bash
   mkdir ecommerce-automation
   cd ecommerce-automation
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Usage

### Task 1: Initial Setup and Navigation

Run the basic navigation and setup:

```bash
python main.py
```

This will:
- Launch Chrome browser in headless mode
- Navigate to bestbuy.com
- Implement robust wait strategies for dynamic elements
- Take a screenshot for verification
- Log all activities

## Configuration

The `config.py` file contains all configuration settings:

- **Browser settings**: Headless mode, viewport size, user agent
- **URLs**: Base URL and category-specific URLs
- **Timeouts**: Navigation, element wait, and default timeouts
- **Rate limiting**: Delays to avoid being blocked
- **Logging**: Log levels and file locations

## Features Implemented

### Task 1 ✅
- [x] Launch Chrome browser in headless mode
- [x] Navigate to bestbuy.com
- [x] Implement robust wait strategy for dynamic elements
- [x] Error handling and logging
- [x] Screenshot capture for verification

### Upcoming Tasks
- [ ] Task 2: Product Category Analysis
- [ ] Task 3: Advanced Data Collection

## Logging

All activities are logged to:
- Console output (for real-time monitoring)
- `logs/automation.log` (for persistent logging)

Log levels include INFO, WARNING, ERROR, and DEBUG messages.

## Error Handling

The system includes comprehensive error handling for:
- Browser launch failures
- Navigation timeouts
- Element not found scenarios
- Network connectivity issues
- Resource cleanup

## Screenshots

Screenshots are automatically saved to the `data/` directory for verification and debugging purposes.

## Development Notes

- Uses async/await pattern for efficient browser automation
- Implements proper resource cleanup
- Follows clean code practices with type hints
- Comprehensive logging for debugging and monitoring
- Configurable timeouts and delays for reliability 