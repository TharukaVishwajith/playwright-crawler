"""
E-Commerce Analytics Automation - Main Script
Task 1: Initial Setup and Navigation
"""

import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Optional, List, Dict

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError, Playwright

import config


class BestBuyAutomation:
    """Main automation class for Best Buy e-commerce analytics."""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        # Ensure logs directory exists
        config.LOGS_DIR.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, config.LOGGING_CONFIG["level"]),
            format=config.LOGGING_CONFIG["format"],
            handlers=[
                logging.FileHandler(config.LOGGING_CONFIG["filename"]),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def launch_browser(self) -> None:
        """
        Launch Firefox browser in headless mode with robust configuration.
        Task 1: Initial Setup
        Note: Using Firefox instead of Chromium due to system compatibility issues
        """
        try:
            self.logger.info("Launching Firefox browser in headless mode...")
            
            self.playwright = await async_playwright().start()
            
            # Launch Firefox browser with minimal configuration
            self.browser = await self.playwright.firefox.launch(
                headless=config.BROWSER_CONFIG["headless"]
            )
            
            # Create browser context with viewport and user agent
            self.context = await self.browser.new_context(
                viewport=config.BROWSER_CONFIG["viewport"],
                user_agent=config.BROWSER_CONFIG["user_agent"]
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Set default timeouts
            self.page.set_default_timeout(config.DEFAULT_TIMEOUT)
            self.page.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)
            
            self.logger.info("Browser launched successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to launch browser: {e}")
            raise
            
    async def navigate_to_bestbuy(self) -> None:
        """
        Navigate to Best Buy website with robust wait strategy.
        Task 1: Navigation
        """
        try:
            self.logger.info(f"Navigating to {config.BASE_URL}...")
            
            # Navigate to Best Buy with wait for load state
            await self.page.goto(
                config.BASE_URL, 
                wait_until="domcontentloaded",
                timeout=config.NAVIGATION_TIMEOUT
            )
            
            # Implement robust wait strategy for dynamic elements
            # await self.wait_for_page_ready()

            await asyncio.sleep(5)
            
            # Handle country selection if it appears
            await self.handle_country_selection()
            
            # Handle location permission alert if it appears
            await self.handle_location_permission()
            
            self.logger.info("Successfully navigated to Best Buy")
            
        except PlaywrightTimeoutError:
            self.logger.error("Timeout while navigating to Best Buy")
            raise
        except Exception as e:
            self.logger.error(f"Failed to navigate to Best Buy: {e}")
            raise
            
    async def handle_country_selection(self) -> None:
        """
        Handle the country selection screen if it appears.
        Looks for "Choose a country." H1 and clicks on "United States" H4.
        """
        try:
            self.logger.info("Checking for country selection screen...")
            
            # Check if the country selection screen is present
            country_selection_header = await self.page.query_selector('h1:has-text("Choose a country.")')
            
            if country_selection_header:
                self.logger.info("Country selection screen detected")
                
                # Look for the United States option
                us_option = await self.page.query_selector('h4:has-text("United States")')
                
                if us_option:
                    self.logger.info("Clicking on United States option...")
                    
                    # Click on the United States option
                    await us_option.click()
                    
                    # Wait for navigation after clicking
                    await self.page.wait_for_load_state("domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
                    
                    # Wait for the new page to be ready
                    await self.wait_for_page_ready()
                    
                    self.logger.info("Successfully selected United States and navigated to main site")
                else:
                    self.logger.warning("United States option not found on country selection screen")
            else:
                self.logger.info("No country selection screen detected, proceeding with main site")
                
        except Exception as e:
            self.logger.error(f"Error handling country selection: {e}")
            # Don't raise the exception as this might not be critical
            self.logger.info("Continuing despite country selection handling error...")
            
    async def handle_location_permission(self) -> None:
        """
        Handle location permission alert/dialog if it appears.
        This can be a browser dialog or a website popup asking for location access.
        """
        try:
            self.logger.info("Checking for location permission dialog...")
            
            # Grant geolocation permission at browser context level
            await self.context.grant_permissions(['geolocation'])
            self.logger.info("Granted geolocation permission at browser context level")
            
            # Set up dialog handler for browser-level dialogs
            dialog_occurred = False
            
            async def dialog_handler(dialog):
                nonlocal dialog_occurred
                dialog_occurred = True
                self.logger.info(f"Dialog detected: {dialog.type} - {dialog.message}")
                try:
                    if dialog.type in ['alert', 'confirm'] and any(keyword in dialog.message.lower() for keyword in ['location', 'allow', 'permission', 'enable']):
                        self.logger.info("Accepting location-related dialog")
                        await dialog.accept()
                    else:
                        self.logger.info("Accepting dialog")
                        await dialog.accept()
                except Exception as e:
                    self.logger.error(f"Error handling dialog: {e}")
                    try:
                        await dialog.dismiss()
                    except:
                        pass
            
            # Add dialog listener
            self.page.on("dialog", dialog_handler)
            
            # Wait for potential dialogs and page popups
            await asyncio.sleep(3)
            
            # Check for common location permission selectors on the page
            location_selectors = [
                # Common location permission buttons
                'button:has-text("Allow")',
                'button:has-text("Block")',
                'button:has-text("Enable Location")',
                'button:has-text("Share Location")',
                'button:has-text("Not now")',
                'button:has-text("Later")',
                '[data-testid*="location"]',
                '[class*="location"]',
                '.location-permission button',
                '[aria-label*="location"]',
                'button[class*="location"]',
                # Generic modal/popup close buttons
                'button[aria-label="Close"]',
                'button[aria-label="close"]',
                '.modal button',
                '.popup button',
                '[role="dialog"] button',
                '.notification button',
                # Common dismiss patterns
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
                'button:has-text("X")',
                '.close-button',
                '.dismiss-button'
            ]
            
            popup_handled = False
            for selector in location_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            text_content = await element.text_content() or ""
                            self.logger.info(f"Found potential popup element: {text_content.strip()}")
                            
                            # Click allow/enable buttons or dismiss buttons
                            if any(keyword in text_content.lower() for keyword in ['allow', 'enable', 'share', 'dismiss', 'close', 'not now', 'later', 'block']):
                                self.logger.info(f"Clicking location permission/popup button: {text_content.strip()}")
                                await element.click()
                                popup_handled = True
                                # Wait for popup to disappear
                                await asyncio.sleep(2)
                                break
                            # Handle X or close buttons
                            elif text_content.strip() in ['X', '×', ''] and 'close' in selector.lower():
                                self.logger.info(f"Clicking close button")
                                await element.click()
                                popup_handled = True
                                await asyncio.sleep(2)
                                break
                                
                    if popup_handled:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Selector {selector} not found or not clickable: {e}")
                    continue
            
            # Try to dismiss any remaining overlays by pressing Escape
            if not popup_handled and not dialog_occurred:
                self.logger.info("No popup buttons found, trying Escape key to dismiss overlays")
                await self.page.keyboard.press('Escape')
                await asyncio.sleep(1)
            
            # Remove dialog listener
            self.page.remove_listener("dialog", dialog_handler)
            
            # Take a screenshot to see current state
            try:
                await self.take_screenshot("after_location_handling.png")
            except:
                pass
            
            self.logger.info("Location permission handling completed")
            
        except Exception as e:
            self.logger.error(f"Error handling location permission: {e}")
            # Don't raise the exception as this might not be critical
            self.logger.info("Continuing despite location permission handling error...")
            
    async def wait_for_page_ready(self) -> None:
        """
        Implement robust wait strategy for dynamic elements.
        Task 1: Robust wait strategy
        """
        try:
            self.logger.info("Waiting for page to be fully loaded...")
            
            # Wait for network to be idle (reduced timeout for faster execution)
            try:
                await self.page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info("Network is idle")
            except Exception as e:
                self.logger.warning(f"Network idle timeout: {e}")
            
            # Wait for common Best Buy elements to ensure page is loaded
            selectors_to_wait = [
                'header',                 # Main header (simplified selector)
                'nav',                    # Navigation menu
                'main, #main, [role="main"]',  # Main content area with fallbacks
            ]
            
            elements_found = 0
            for selector in selectors_to_wait:
                try:
                    await self.page.wait_for_selector(
                        selector, 
                        timeout=config.ELEMENT_WAIT_TIMEOUT,
                        state="visible"
                    )
                    self.logger.debug(f"Found element: {selector}")
                    elements_found += 1
                except Exception as e:
                    self.logger.warning(f"Element not found within timeout: {selector} - {e}")
            
            # Continue if we found at least one element
            if elements_found > 0:
                self.logger.info(f"Found {elements_found} out of {len(selectors_to_wait)} expected elements")
            else:
                self.logger.warning("No expected elements found, but continuing...")
            
            # Additional wait for any dynamic content
            await asyncio.sleep(config.PAGE_LOAD_DELAY)
            
            # Verify we're on the correct site
            current_url = self.page.url
            if "bestbuy.com" not in current_url:
                raise Exception(f"Unexpected URL: {current_url}")
                
            self.logger.info("Page is fully loaded and ready")
            
        except Exception as e:
            self.logger.error(f"Error waiting for page ready: {e}")
            raise
            
    async def take_screenshot(self, filename: str = "task1_screenshot.png") -> None:
        """Take a screenshot for verification purposes."""
        try:
            screenshot_path = config.DATA_DIR / filename
            config.DATA_DIR.mkdir(exist_ok=True)
            
            await self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            
    async def get_page_info(self) -> dict:
        """Get basic page information for verification."""
        try:
            page_info = {
                "url": self.page.url,
                "title": await self.page.title(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.logger.info(f"Page info: {page_info}")
            return page_info
            
        except Exception as e:
            self.logger.error(f"Failed to get page info: {e}")
            return {}
            
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.info("Browser cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    async def search_laptops_and_filter(self) -> None:
        """
        Perform laptop search and apply price filtering.
        Steps:
        1. Search for "laptop"
        2. Wait for results to load
        3. Set price range (500-1500)
        4. Apply the filter
        """
        try:
            self.logger.info("=== Starting laptop search and price filtering ===")
            
            # Debug: Take a screenshot to see current page state
            await self.take_screenshot("before_search.png")
            
            # Step 1: Type "laptop" in the search input field with multiple selector options
            self.logger.info("Step 1: Searching for 'laptop'...")
            
            search_selectors = [
                'input.sugg-search-bar-input[data-testid="SearchBar-TestID"]',
                'input[data-testid="SearchBar-TestID"]',
                'input[placeholder*="Search"]',
                'input[id*="search"]',
                'input[class*="search"]',
                'input[autocomplete-search-bar]',
                '#autocomplete-search-bar',
                'input.search-input',
                '[role="searchbox"]',
                'input[type="search"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    self.logger.info(f"Trying search selector: {selector}")
                    search_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if search_input:
                        self.logger.info(f"Found search input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Search selector {selector} failed: {e}")
                    continue
            
            if not search_input:
                # Debug: Print available input elements
                self.logger.info("Search input not found, checking all input elements...")
                inputs = await self.page.query_selector_all('input')
                for i, input_elem in enumerate(inputs):
                    try:
                        if await input_elem.is_visible():
                            placeholder = await input_elem.get_attribute('placeholder') or ''
                            id_attr = await input_elem.get_attribute('id') or ''
                            class_attr = await input_elem.get_attribute('class') or ''
                            self.logger.info(f"Input {i}: placeholder='{placeholder}', id='{id_attr}', class='{class_attr}'")
                    except:
                        pass
                raise Exception("Search input field not found")
            
            # Clear any existing text and type "laptop"
            await search_input.fill("laptop")
            self.logger.info("Typed 'laptop' in search field")
            
            # Step 2: Click the search button with multiple selector options
            self.logger.info("Step 2: Clicking search button...")
            
            button_selectors = [
                'button#autocomplete-search-button[data-testid="SearchButton-TestID"]',
                'button[data-testid="SearchButton-TestID"]',
                'button[aria-label*="Search"]',
                'button.sugg-magnifier',
                'button[id*="search"]',
                'button[class*="search"]',
                '[role="button"][aria-label*="Search"]',
                'button:has-text("Search")',
                '.search-button'
            ]
            
            search_button = None
            for selector in button_selectors:
                try:
                    self.logger.info(f"Trying button selector: {selector}")
                    search_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if search_button:
                        self.logger.info(f"Found search button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Button selector {selector} failed: {e}")
                    continue
            
            if not search_button:
                # Alternative: Press Enter on the search input
                self.logger.info("Search button not found, trying Enter key...")
                await search_input.press('Enter')
            else:
                await search_button.click()
            
            self.logger.info("Search submitted")
            
            # Step 3: Wait 15 seconds for the page to load
            self.logger.info("Step 3: Waiting 5 seconds for search results to load...")
            await asyncio.sleep(5)
            
            # Additional wait for page to be ready
            await self.page.wait_for_load_state("domcontentloaded")
            self.logger.info("Search results page loaded")
            
            # Debug: Take screenshot of search results
            await self.take_screenshot("search_results.png")
            
            # Step 4: Set minimum price to 500
            self.logger.info("Step 4: Setting minimum price to 500...")
            
            min_price_selectors = [
                'input[placeholder="Min Price"]',
                'input[placeholder*="Min"]',
                'input[data-testid*="min"]',
                'input[aria-label*="minimum"]',
                '.price-filter input[type="number"]:first-child',
                '.min-price input'
            ]
            
            min_price_input = None
            for selector in min_price_selectors:
                try:
                    min_price_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if min_price_input:
                        self.logger.info(f"Found min price input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Min price selector {selector} failed: {e}")
                    continue
            
            if not min_price_input:
                raise Exception("Min price input field not found")
                
            await min_price_input.fill("500")
            self.logger.info("Set minimum price to 500")
            
            # Step 5: Set maximum price to 1500
            self.logger.info("Step 5: Setting maximum price to 1500...")
            
            max_price_selectors = [
                'input[placeholder="Max Price"]',
                'input[placeholder*="Max"]',
                'input[data-testid*="max"]',
                'input[aria-label*="maximum"]',
                '.price-filter input[type="number"]:last-child',
                '.max-price input'
            ]
            
            max_price_input = None
            for selector in max_price_selectors:
                try:
                    max_price_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if max_price_input:
                        self.logger.info(f"Found max price input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Max price selector {selector} failed: {e}")
                    continue
            
            if not max_price_input:
                raise Exception("Max price input field not found")
                
            await max_price_input.fill("1500")
            self.logger.info("Set maximum price to 1500")
            
            # Step 6: Click the "Set" button to apply price filter
            self.logger.info("Step 6: Applying price filter...")
            
            set_button_selectors = [
                'button.current-price-facet-set-button:has-text("Set")',
                'button:has-text("Set")',
                'button[aria-label*="Set"]',
                '.price-filter button:has-text("Set")',
                '.price-facet button:has-text("Set")',
                'button.set-button'
            ]
            
            set_button = None
            for selector in set_button_selectors:
                try:
                    set_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if set_button:
                        self.logger.info(f"Found set button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Set button selector {selector} failed: {e}")
                    continue
            
            if not set_button:
                raise Exception("Set button not found")
                
            await set_button.click()
            self.logger.info("Clicked 'Set' button to apply price filter")
            
            # Wait for filter to be applied
            await asyncio.sleep(3)
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Final screenshot
            await self.take_screenshot("final_filtered_results.png")
            
            self.logger.info("=== Laptop search and price filtering completed successfully ===")
            
        except Exception as e:
            self.logger.error(f"Error during laptop search and filtering: {e}")
            # Take screenshot for debugging
            try:
                await self.take_screenshot("error_state.png")
            except:
                pass
            raise
            
    async def apply_brand_filters_and_load_data(self) -> None:
        """
        Apply brand filters and perform lazy loading.
        Steps:
        1. Check first 3 brand checkboxes
        2. Check customer rating checkbox (4 & Up)
        3. Wait for filters to be applied
        4. Scroll down to load all data (lazy loading)
        """
        try:
            self.logger.info("=== Starting brand filter application and data loading ===")
            
            # Step 1: Find and check the first 3 brand checkboxes
            self.logger.info("Step 1: Checking first 3 brand filter checkboxes...")
            
            # Wait for the brand facet section to be available
            brand_section = await self.page.wait_for_selector(
                'section.facet[data-facet="brand_facet"]',
                timeout=10000,
                state="visible"
            )
            self.logger.info("Found brand facet section")
            
            # Find all checkboxes within the brand facet section
            brand_checkboxes = await brand_section.query_selector_all('input[type="checkbox"]')
            self.logger.info(f"Found {len(brand_checkboxes)} brand checkboxes")
            
            # Check the first 3 checkboxes
            checkboxes_to_check = min(3, len(brand_checkboxes))
            for i in range(checkboxes_to_check):
                checkbox = brand_checkboxes[i]
                
                # Check if the checkbox is already checked
                is_checked = await checkbox.is_checked()
                if not is_checked:
                    # Get the brand name for logging
                    try:
                        # Look for associated label text
                        checkbox_id = await checkbox.get_attribute('id')
                        if checkbox_id:
                            label = await self.page.query_selector(f'label[for="{checkbox_id}"]')
                            if label:
                                brand_name = await label.text_content()
                                self.logger.info(f"Checking brand filter {i+1}: {brand_name.strip()}")
                            else:
                                self.logger.info(f"Checking brand filter {i+1}")
                        else:
                            self.logger.info(f"Checking brand filter {i+1}")
                    except:
                        self.logger.info(f"Checking brand filter {i+1}")
                    
                    # Click the checkbox
                    await checkbox.click()
                    
                    # Small delay between clicks
                    await asyncio.sleep(0.5)
                else:
                    self.logger.info(f"Brand filter {i+1} is already checked")
            
            self.logger.info(f"Successfully checked {checkboxes_to_check} brand filters")

            # Step 2: Check customer rating checkbox (4 & Up)
            self.logger.info("Step 2: Checking customer rating filter (4 & Up)...")
            
            # Wait for the rating checkbox to be available
            rating_checkbox = await self.page.wait_for_selector(
                'input[type="checkbox"][id="customer-rating-4_&_Up"]',
                timeout=10000,
                state="visible"
            )
            
            if rating_checkbox:
                # Check if the checkbox is already checked
                is_checked = await rating_checkbox.is_checked()
                if not is_checked:
                    self.logger.info("Checking customer rating filter (4 & Up)")
                    await rating_checkbox.click()
                    await asyncio.sleep(0.5)
                else:
                    self.logger.info("Customer rating filter is already checked")
            else:
                self.logger.warning("Customer rating checkbox not found")
            
            # Step 3: Wait for filters to be applied
            self.logger.info("Step 3: Waiting for filters to be applied...")
            
            # Wait for page to process the filter changes
            await asyncio.sleep(3)
            
            # Wait for network activity to settle
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
                self.logger.info("Network activity settled after filter application")
            except Exception as e:
                self.logger.warning(f"Network idle timeout after filters: {e}")
            
            # Take screenshot after filters applied
            await self.take_screenshot("after_filters.png")
            
            # Step 4: Enhanced slow scrolling for lazy loading
            await self.slow_scroll_to_load_all_content()
            
            # Take final screenshot showing all loaded content
            await self.take_screenshot("final_with_filters_and_data.png")
            
            self.logger.info("=== Filter application and data loading completed successfully ===")
            
        except Exception as e:
            self.logger.error(f"Error during filter application and data loading: {e}")
            # Take screenshot for debugging
            try:
                await self.take_screenshot("filter_error_state.png")
            except:
                pass
            raise
            
    async def run_task_1(self) -> dict:
        """
        Execute Task 1: Initial Setup and Navigation
        Returns page information for verification
        """
        try:
            self.logger.info("=== Starting Task 1: Initial Setup and Navigation ===")
            
            # Launch browser
            await self.launch_browser()
            
            # Navigate to Best Buy
            await self.navigate_to_bestbuy()
            
            # Perform laptop search and price filtering
            await self.search_laptops_and_filter()
            
            # Apply brand filters and load all data
            await self.apply_brand_filters_and_load_data()
            
            # Scrape product details from all pages
            products = await self.scrape_all_pages_products()
            
            # Save products to JSON file
            await self.save_products_to_json(products, "laptop_products_all_pages.json")
            
            # Take final screenshot for verification
            await self.take_screenshot("task1_laptop_search_filtered_final.png")
            
            # Get page information
            page_info = await self.get_page_info()
            page_info["products_scraped"] = len(products)
            
            self.logger.info("=== Task 1 completed successfully ===")
            return page_info
            
        except Exception as e:
            self.logger.error(f"Task 1 failed: {e}")
            raise
        finally:
            await self.cleanup()

    async def slow_scroll_to_load_all_content(self) -> None:
        """
        Enhanced slow scrolling to handle lazy-loaded content.
        Uses progressive scrolling with multiple detection methods to ensure all content loads.
        """
        try:
            self.logger.info("Step 3: Starting enhanced slow scrolling for lazy loading...")
            
            # Get initial state
            initial_height = await self.page.evaluate("document.body.scrollHeight")
            self.logger.info(f"Initial page height: {initial_height}px")
            
            # Initialize tracking variables using config values
            scroll_position = 0
            scroll_step = config.LAZY_LOADING_CONFIG["scroll_step"]
            max_scroll_attempts = config.LAZY_LOADING_CONFIG["max_scroll_attempts"]
            stagnant_attempts = 0
            max_stagnant_attempts = config.LAZY_LOADING_CONFIG["max_stagnant_attempts"]
            pagination_found = False
            content_stabilized = False
            
            # Track content metrics for stability detection
            previous_height = initial_height
            height_stable_count = 0
            required_stable_count = config.LAZY_LOADING_CONFIG["stability_check_count"]
            
            while stagnant_attempts < max_stagnant_attempts and not content_stabilized:
                # Check for pagination container (main end-of-content indicator)
                try:
                    pagination_selectors = [
                        'div.pagination-container',
                        '.pagination',
                        '[data-testid*="pagination"]',
                        '.paging-content',
                        '.page-numbers'
                    ]
                    
                    for selector in pagination_selectors:
                        pagination_element = await self.page.query_selector(selector)
                        if pagination_element and await pagination_element.is_visible():
                            self.logger.info(f"Pagination container found with selector: {selector}")
                            pagination_found = True
                            break
                    
                    if pagination_found:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Error checking pagination: {e}")
                
                # Check for loading indicators before scrolling
                await self.wait_for_loading_indicators()
                
                # Perform gradual scroll
                current_height = await self.page.evaluate("document.body.scrollHeight")
                
                if scroll_position < current_height:
                    # Calculate next scroll position
                    scroll_position = min(scroll_position + scroll_step, current_height)
                    
                    self.logger.info(f"Scrolling to position: {scroll_position}px (page height: {current_height}px)")
                    
                    # Smooth scroll to position
                    await self.page.evaluate(f"""
                        window.scrollTo({{
                            top: {scroll_position},
                            behavior: 'smooth'
                        }});
                    """)
                    
                    # Wait for scroll to complete and content to potentially load
                    await asyncio.sleep(config.LAZY_LOADING_CONFIG["scroll_delay"])
                    
                    # Wait for any loading indicators that might appear
                    await self.wait_for_loading_indicators()
                    
                    # Additional wait for network activity
                    try:
                        await self.page.wait_for_load_state("networkidle", timeout=config.LAZY_LOADING_CONFIG["network_idle_timeout"])
                    except Exception:
                        pass  # Continue if network doesn't idle quickly
                    
                else:
                    # Reached bottom, check if height changed
                    new_height = await self.page.evaluate("document.body.scrollHeight")
                    
                    if new_height > previous_height:
                        self.logger.info(f"New content loaded! Height: {previous_height}px → {new_height}px")
                        previous_height = new_height
                        height_stable_count = 0
                        stagnant_attempts = 0  # Reset stagnant counter
                        
                        # Continue scrolling with new content
                        continue
                    else:
                        height_stable_count += 1
                        self.logger.info(f"Height stable ({height_stable_count}/{required_stable_count}): {new_height}px")
                        
                        if height_stable_count >= required_stable_count:
                            content_stabilized = True
                            self.logger.info("Content has stabilized - no new content loading")
                            break
                        
                        stagnant_attempts += 1
                        
                        # Try scrolling to absolute bottom and wait longer
                        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(config.LAZY_LOADING_CONFIG["final_wait_time"])
                        
                        # Check for infinite scroll triggers
                        await self.check_for_infinite_scroll_triggers()
            
            # Final status report
            final_height = await self.page.evaluate("document.body.scrollHeight")
            self.logger.info(f"Lazy loading completed:")
            self.logger.info(f"  - Initial height: {initial_height}px")
            self.logger.info(f"  - Final height: {final_height}px")
            self.logger.info(f"  - Height increase: {final_height - initial_height}px")
            self.logger.info(f"  - Pagination found: {pagination_found}")
            self.logger.info(f"  - Content stabilized: {content_stabilized}")
            
            # Position page for optimal visibility
            if pagination_found:
                # Scroll to show pagination
                await self.page.evaluate("""
                    const pagination = document.querySelector('div.pagination-container, .pagination, [data-testid*="pagination"]');
                    if (pagination) {
                        pagination.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                """)
                await asyncio.sleep(2)
                await self.take_screenshot("pagination_container_found.png")
            
            # Scroll back to top for final screenshot
            await self.page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
            await asyncio.sleep(2)

            # Additional 10-second wait to ensure all data is loaded
            self.logger.info("Waiting 10 seconds to ensure all data is fully loaded...")
            await asyncio.sleep(10)
            self.logger.info("10-second wait completed")
            await self.take_screenshot("page_01_after_lazy_loading.png")
            
        except Exception as e:
            self.logger.error(f"Error during slow scroll lazy loading: {e}")
            raise

    async def wait_for_loading_indicators(self) -> None:
        """
        Wait for any visible loading indicators to disappear.
        """
        try:
            loading_selectors = [
                '[class*="loading"]',
                '[class*="spinner"]',
                '[class*="loader"]',
                '[data-testid*="loading"]',
                '.loading-overlay',
                '.spinner-container',
                '[aria-live="polite"]',  # Often used for loading announcements
                '.skeleton-loader',
                '.lazy-loading'
            ]
            
            max_wait_time = config.LAZY_LOADING_CONFIG["loading_indicator_timeout"]
            check_interval = 0.5
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                visible_loaders = []
                
                for selector in loading_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for element in elements:
                            if await element.is_visible():
                                visible_loaders.append(selector)
                                break
                    except Exception:
                        continue
                
                if not visible_loaders:
                    break
                
                self.logger.info(f"Waiting for loading indicators: {visible_loaders}")
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            if elapsed_time >= max_wait_time:
                self.logger.warning("Timeout waiting for loading indicators to disappear")
            
        except Exception as e:
            self.logger.debug(f"Error checking loading indicators: {e}")

    async def check_for_infinite_scroll_triggers(self) -> None:
        """
        Check for and trigger infinite scroll mechanisms.
        """
        try:
            # Look for "Load More" buttons
            load_more_selectors = [
                'button:has-text("Load More")',
                'button:has-text("Show More")',
                'button:has-text("View More")',
                '[data-testid*="load-more"]',
                '[class*="load-more"]',
                '.show-more-button',
                '.load-more-products'
            ]
            
            for selector in load_more_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button and await button.is_visible():
                        self.logger.info(f"Found load more button: {selector}")
                        await button.click()
                        await asyncio.sleep(2)
                        return
                except Exception:
                    continue
            
            # Trigger scroll events that might activate lazy loading
            await self.page.evaluate("""
                // Dispatch scroll events to trigger lazy loading
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
                
                // Try to find and trigger intersection observers
                const sentinels = document.querySelectorAll('[class*="sentinel"], [class*="trigger"], [data-scroll-trigger]');
                sentinels.forEach(sentinel => {
                    sentinel.scrollIntoView({ block: 'center' });
                });
            """)
            
        except Exception as e:
            self.logger.debug(f"Error checking infinite scroll triggers: {e}")

    async def slow_scroll_page(self, page_number: int) -> None:
        """
        Perform slow scrolling from top to bottom over 20 seconds for a single page.
        This ensures all lazy-loaded content is properly loaded.
        """
        try:
            self.logger.info(f"Starting slow scroll on page {page_number} (20 seconds)...")
            
            # Start from the top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
            # Get page height
            page_height = await self.page.evaluate("document.body.scrollHeight")
            self.logger.info(f"Page {page_number} height: {page_height}px")
            
            # Calculate scroll parameters for 20 seconds
            scroll_duration = 20  # seconds
            scroll_steps = 40  # number of scroll steps (20 seconds / 0.5 second intervals)
            step_delay = scroll_duration / scroll_steps  # 0.5 seconds per step
            scroll_step_size = page_height / scroll_steps  # pixels per step
            
            current_position = 0
            
            for step in range(scroll_steps):
                # Calculate next scroll position
                next_position = min(current_position + scroll_step_size, page_height)
                
                # Smooth scroll to next position
                await self.page.evaluate(f"""
                    window.scrollTo({{
                        top: {next_position},
                        behavior: 'smooth'
                    }});
                """)
                
                current_position = next_position
                
                # Log progress every 5 seconds (every 10 steps)
                if step % 10 == 0:
                    progress = (step / scroll_steps) * 100
                    self.logger.info(f"Page {page_number} scroll progress: {progress:.0f}% ({next_position:.0f}px)")
                
                # Wait between scroll steps
                await asyncio.sleep(step_delay)
                
                # Check if we've reached the bottom
                if next_position >= page_height:
                    break
            
            # Ensure we're at the bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Scroll back to top for consistent scraping
            self.logger.info(f"Scrolling back to top of page {page_number}...")
            await self.page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
            await asyncio.sleep(3)
            
            self.logger.info(f"Slow scroll completed for page {page_number}")
            
        except Exception as e:
            self.logger.error(f"Error during slow scroll on page {page_number}: {e}")
            # Continue anyway - don't let scroll issues stop the scraping
            
    async def scrape_all_pages_products(self) -> List[Dict]:
        """
        Scrape product details from all pages by navigating through pagination.
        Returns a consolidated list of all products from all pages.
        """
        try:
            self.logger.info("=== Starting multi-page product scraping ===")
            
            all_products = []
            current_page = 1
            max_pages = 5  # Safety limit to prevent infinite loops
            
            while current_page <= max_pages:
                self.logger.info(f"Scraping page {current_page}...")
                
                # Wait for page to be ready
                await asyncio.sleep(3)
                await self.page.wait_for_load_state("domcontentloaded")
                
                # Perform slow scroll from top to bottom over 20 seconds
                await self.slow_scroll_page(current_page)
                
                # Scrape products from current page
                try:
                    page_products = await self.scrape_product_details()
                    if page_products:
                        all_products.extend(page_products)
                        self.logger.info(f"Page {current_page}: Found {len(page_products)} products (Total: {len(all_products)})")
                    else:
                        self.logger.warning(f"Page {current_page}: No products found")
                except Exception as e:
                    self.logger.error(f"Error scraping page {current_page}: {e}")
                
                # Take screenshot of current page
                await self.take_screenshot(f"page_{current_page:02d}_products.png")
                
                # Look for "Next page" link
                try:
                    next_page_selectors = [
                        'a[aria-label="Next page"]',
                        'a[aria-label="next page"]',
                        'a[aria-label="Next"]',
                        '.pagination a:has-text("Next")',
                        '.pagination a[aria-label*="Next"]',
                        'a.next-page',
                        'a[title*="Next"]'
                    ]
                    
                    next_page_link = None
                    for selector in next_page_selectors:
                        try:
                            next_page_link = await self.page.wait_for_selector(
                                selector,
                                timeout=5000,
                                state="visible"
                            )
                            if next_page_link:
                                # Check if the link is actually clickable (not disabled)
                                is_disabled = await next_page_link.get_attribute('aria-disabled')
                                classes = await next_page_link.get_attribute('class') or ''
                                
                                if is_disabled == 'true' or 'disabled' in classes.lower():
                                    self.logger.info(f"Next page link found but disabled on page {current_page}")
                                    next_page_link = None
                                    continue
                                else:
                                    self.logger.info(f"Found next page link with selector: {selector}")
                                    break
                        except Exception as e:
                            self.logger.debug(f"Next page selector {selector} failed: {e}")
                            continue
                    
                    if not next_page_link:
                        self.logger.info(f"No more pages found. Completed scraping at page {current_page}")
                        break
                    
                    # Click the next page link
                    self.logger.info(f"Navigating to page {current_page + 1}...")
                    
                    # Scroll to the next page link to ensure it's visible
                    await next_page_link.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    
                    # Click the next page link
                    await next_page_link.click()
                    
                    # Wait for navigation and new page to load
                    await asyncio.sleep(5)
                    await self.page.wait_for_load_state("domcontentloaded")
                    
                    # Wait for product list to be available on new page
                    try:
                        await self.page.wait_for_selector(
                            'ul.plp-product-list',
                            timeout=15000,
                            state="visible"
                        )
                    except Exception as e:
                        self.logger.warning(f"Product list not found on page {current_page + 1}: {e}")
                        break
                    
                    current_page += 1
                    
                except Exception as e:
                    self.logger.error(f"Error navigating to next page from page {current_page}: {e}")
                    break
            
            self.logger.info("=== Multi-page scraping completed ===")
            self.logger.info(f"Total pages scraped: {current_page}")
            self.logger.info(f"Total products found: {len(all_products)}")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Error during multi-page scraping: {e}")
            raise

    async def scrape_product_details(self) -> List[Dict]:
        """
        Scrape product details from the search results page.
        Returns a list of dictionaries containing product information.
        """
        try:
            self.logger.info("=== Starting product details scraping ===")
            
            # Wait for the product list to be available
            product_list = await self.page.wait_for_selector(
                'ul.plp-product-list',
                timeout=10000,
                state="visible"
            )
            
            if not product_list:
                raise Exception("Product list not found")
            
            # Get all product items
            product_items = await product_list.query_selector_all('li.product-list-item')
            self.logger.info(f"Found {len(product_items)} product items to scrape")
            
            products = []
            
            for i, item in enumerate(product_items):
                try:
                    self.logger.info(f"Scraping product {i+1} of {len(product_items)}")
                    
                    # Initialize product data
                    product_data = {
                        "product_name": "",
                        "price": "",
                        "rating": "",
                        "number_of_reviews": "",
                        "url": ""
                    }
                    
                    # Scrape product name from h2 title attribute
                    try:
                        product_title = await item.query_selector('h2.product-title')
                        if product_title:
                            title_attr = await product_title.get_attribute('title')
                            if title_attr:
                                product_data["product_name"] = title_attr.strip()
                            else:
                                # Fallback to text content if title attribute is missing
                                text_content = await product_title.text_content()
                                if text_content:
                                    product_data["product_name"] = text_content.strip()
                    except Exception as e:
                        self.logger.warning(f"Could not extract product name for item {i+1}: {e}")
                    
                    # Scrape price from customer-price div
                    try:
                        price_element = await item.query_selector('div.customer-price')
                        if price_element:
                            price_text = await price_element.text_content()
                            if price_text:
                                product_data["price"] = price_text.strip()
                    except Exception as e:
                        self.logger.warning(f"Could not extract price for item {i+1}: {e}")
                    
                    # Scrape rating from c-stars-container style width
                    try:
                        rating_element = await item.query_selector('span.c-stars-container[style*="width:"]')
                        if rating_element:
                            style_attr = await rating_element.get_attribute('style')
                            if style_attr and 'width:' in style_attr:
                                # Extract percentage from style attribute - handle both direct % and calc() formats
                                import re
                                # First try to match calc(XX% + Xpx) format
                                calc_match = re.search(r'width:\s*calc\((\d+(?:\.\d+)?)%[^)]*\)', style_attr)
                                if calc_match:
                                    percentage = calc_match.group(1)
                                    product_data["rating"] = f"{percentage}%"
                                else:
                                    # Fallback to direct percentage format
                                    direct_match = re.search(r'width:\s*(\d+(?:\.\d+)?)%', style_attr)
                                    if direct_match:
                                        percentage = direct_match.group(1)
                                        product_data["rating"] = f"{percentage}%"
                    except Exception as e:
                        self.logger.warning(f"Could not extract rating for item {i+1}: {e}")
                    
                    # Scrape number of reviews from c-reviews span
                    try:
                        reviews_element = await item.query_selector('span.c-reviews')
                        if reviews_element:
                            reviews_text = await reviews_element.text_content()
                            if reviews_text:
                                # Extract number from parentheses
                                import re
                                match = re.search(r'\(([0-9,]+)\)', reviews_text)
                                if match:
                                    product_data["number_of_reviews"] = match.group(1)
                                else:
                                    product_data["number_of_reviews"] = reviews_text.strip()
                    except Exception as e:
                        self.logger.warning(f"Could not extract reviews for item {i+1}: {e}")
                    
                    # Scrape URL from product-image link
                    try:
                        url_element = await item.query_selector('div.product-image a[href]')
                        if url_element:
                            href = await url_element.get_attribute('href')
                            if href:
                                # Make absolute URL if it's relative
                                if href.startswith('/'):
                                    product_data["url"] = f"https://www.bestbuy.com{href}"
                                else:
                                    product_data["url"] = href
                    except Exception as e:
                        self.logger.warning(f"Could not extract URL for item {i+1}: {e}")
                    
                    # Add product to list if we have at least product name or URL
                    if product_data["product_name"] or product_data["url"]:
                        products.append(product_data)
                        self.logger.info(f"Successfully scraped product {i+1}: {product_data['product_name'][:50]}...")
                    else:
                        self.logger.warning(f"Skipping product {i+1} - insufficient data")
                
                except Exception as e:
                    self.logger.error(f"Error scraping product {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully scraped {len(products)} products")
            return products
            
        except Exception as e:
            self.logger.error(f"Error during product scraping: {e}")
            raise

    async def save_products_to_json(self, products: List[Dict], filename: str = "products.json") -> None:
        """
        Save scraped products to a JSON file.
        """
        try:
            # Ensure data directory exists
            config.DATA_DIR.mkdir(exist_ok=True)
            
            # Create file path
            file_path = config.DATA_DIR / filename
            
            # Save to JSON file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successfully saved {len(products)} products to {file_path}")
            
            # Log summary
            self.logger.info("=== Product Scraping Summary ===")
            self.logger.info(f"Total products scraped: {len(products)}")
            self.logger.info(f"JSON file saved: {file_path}")
            
            # Print first few products for verification
            if products:
                self.logger.info("First product sample:")
                first_product = products[0]
                for key, value in first_product.items():
                    self.logger.info(f"  {key}: {value}")
            
        except Exception as e:
            self.logger.error(f"Error saving products to JSON: {e}")
            raise

    async def load_products_from_json(self, filename: str = "laptop_products_all_pages.json") -> List[Dict]:
        """
        Load products from existing JSON file.
        """
        try:
            file_path = config.DATA_DIR / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Products file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            self.logger.info(f"Successfully loaded {len(products)} products from {file_path}")
            return products
            
        except Exception as e:
            self.logger.error(f"Error loading products from JSON: {e}")
            raise

    async def scrape_product_reviews(self, product_url: str, product_name: str) -> Dict:
        """
        Navigate to a product page, scrape specifications and customer reviews.
        Handles pagination to get reviews from all pages.
        
        Args:
            product_url: The URL of the product page
            product_name: Name of the product (for logging)
            
        Returns:
            Dictionary with product specs and reviews
        """
        try:
            self.logger.info(f"Scraping product data for: {product_name[:50]}...")
            
            # Navigate to product page
            await self.page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Handle country selection if it appears
            await self.handle_country_selection()
            
            # Handle location permission if it appears
            await self.handle_location_permission()
            
            # First, extract product specifications
            product_specs = await self.extract_product_specifications(product_name)
            
            # Scroll down to 75% of the page to load the "See All Customer Reviews" button
            self.logger.info("Scrolling down to 75% of page to load review elements...")
            await self.page.evaluate("""
                const scrollHeight = document.body.scrollHeight;
                const scrollTo = scrollHeight * 0.75;
                window.scrollTo({
                    top: scrollTo,
                    behavior: 'smooth'
                });
            """)
            
            # Wait 10 seconds for the button to load
            self.logger.info("Waiting 10 seconds for review elements to load...")
            await asyncio.sleep(10)
            
            # Wait for network activity to settle
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass  # Continue if network doesn't idle quickly
            
            # Look for "See All Customer Reviews" button with more specific selectors
            review_button_selectors = [
                'button:has-text("See All Customer Reviews")',
                'button[aria-label*="See All Customer Reviews"]',
                'a:has-text("See All Customer Reviews")',
                'button.relative.border-xs:has-text("See All Customer Reviews")',
                '[role="link"]:has-text("See All Customer Reviews")',
                'button[class*="relative"][class*="border"]:has-text("See All Customer Reviews")',
                '[class*="Op9coqeII1kYHR9Q"]:has-text("See All Customer Reviews")',
                'button:text("See All Customer Reviews")',
                'a:text("See All Customer Reviews")'
            ]
            
            review_button = None
            for selector in review_button_selectors:
                try:
                    self.logger.debug(f"Trying review button selector: {selector}")
                    review_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if review_button:
                        self.logger.info(f"Found review button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Review button selector {selector} failed: {e}")
                    continue
            
            # If button not found, try searching for it in the entire page
            if not review_button:
                self.logger.info("Button not found with standard selectors, searching entire page...")
                
                # Get all buttons and links and check their text content
                all_buttons = await self.page.query_selector_all('button, a, [role="button"], [role="link"]')
                for button in all_buttons:
                    try:
                        text_content = await button.text_content()
                        if text_content and "See All Customer Reviews" in text_content:
                            if await button.is_visible():
                                review_button = button
                                self.logger.info(f"Found review button by text search: {text_content.strip()}")
                                break
                    except Exception:
                        continue
            
            if not review_button:
                self.logger.warning(f"Reviews button not found for product: {product_name[:50]}...")
                
                # Take a screenshot for debugging
                await self.take_screenshot(f"no_review_button_{product_name[:20].replace(' ', '_')}.png")
                
                # Return with specs but no reviews
                return {
                    "product_specs": product_specs,
                    "reviews": []
                }
            
            # Scroll the button into view and click it
            self.logger.info("Scrolling review button into view...")
            await review_button.scroll_into_view_if_needed()
            await asyncio.sleep(2)
            
            # Click the reviews button
            self.logger.info("Clicking 'See All Customer Reviews' button...")
            await review_button.click()
            
            # Wait for reviews page to load
            await asyncio.sleep(5)
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Wait for reviews list to be available
            try:
                reviews_list = await self.page.wait_for_selector(
                    'ul.reviews-list',
                    timeout=10000,
                    state="visible"
                )
            except Exception as e:
                self.logger.warning(f"Reviews list not found for product: {product_name[:50]}... - {e}")
                
                # Take screenshot for debugging
                await self.take_screenshot(f"no_reviews_list_{product_name[:20].replace(' ', '_')}.png")
                
                # Return with specs but no reviews
                return {
                    "product_specs": product_specs,
                    "reviews": []
                }
            
            # Scrape reviews from all pages (handle pagination)
            all_reviews = []
            page_number = 1
            max_pages = 10  # Safety limit to prevent infinite loops
            
            while page_number <= max_pages:
                self.logger.info(f"Scraping reviews from page {page_number} for: {product_name[:50]}...")
                
                # Get reviews from current page
                page_reviews = await self.scrape_reviews_from_current_page()
                
                if page_reviews:
                    all_reviews.extend(page_reviews)
                    self.logger.info(f"Found {len(page_reviews)} reviews on page {page_number}")
                else:
                    self.logger.info(f"No reviews found on page {page_number}")
                
                # Check for next page button
                next_button = await self.find_next_page_button()
                
                if next_button:
                    self.logger.info(f"Found next page button, navigating to page {page_number + 1}...")
                    
                    # Click next page button
                    await next_button.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await next_button.click()
                    
                    # Wait for new page to load
                    await asyncio.sleep(3)
                    await self.page.wait_for_load_state("domcontentloaded")
                    
                    # Wait for reviews list to be updated
                    try:
                        await self.page.wait_for_selector('ul.reviews-list', timeout=5000)
                    except Exception:
                        self.logger.warning("Reviews list not found after pagination")
                        break
                    
                    page_number += 1
                else:
                    self.logger.info(f"No more pages found. Completed scraping at page {page_number}")
                    break
            
            self.logger.info(f"Successfully scraped {len(all_reviews)} reviews from {page_number} page(s) for: {product_name[:50]}...")
            
            # Take screenshot of final reviews page for verification
            if all_reviews:
                await self.take_screenshot(f"reviews_found_{product_name[:20].replace(' ', '_')}.png")
            
            # Return combined data
            return {
                "product_specs": product_specs,
                "reviews": all_reviews
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping product data for {product_name[:50]}...: {e}")
            # Take screenshot for debugging
            try:
                await self.take_screenshot(f"error_scraping_{product_name[:20].replace(' ', '_')}.png")
            except:
                pass
            return {
                "product_specs": {},
                "reviews": []
            }

    async def extract_product_specifications(self, product_name: str) -> Dict:
        """
        Extract product specifications by clicking the specifications button and parsing the slide panel.
        
        Args:
            product_name: Name of the product (for logging)
            
        Returns:
            Dictionary containing product specifications
        """
        try:
            self.logger.info(f"Extracting specifications for: {product_name[:50]}...")
            
            # Look for the specifications button using data-testid
            specs_button_selectors = [
                'button[data-testid="brix-button"]',
                'button[data-testid="brix-button"]:has-text("Specifications")',
                'button.c-button-unstyled[data-testid="brix-button"]'
            ]
            
            specs_button = None
            for selector in specs_button_selectors:
                try:
                    specs_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if specs_button:
                        # Check if this button contains "Specifications" text
                        button_text = await specs_button.text_content()
                        if button_text and "Specifications" in button_text:
                            self.logger.info(f"Found specifications button with selector: {selector}")
                            break
                        else:
                            specs_button = None
                except Exception as e:
                    self.logger.debug(f"Specs button selector {selector} failed: {e}")
                    continue
            
            if not specs_button:
                self.logger.warning(f"Specifications button not found for product: {product_name[:50]}...")
                return {}
            
            # Click the specifications button
            self.logger.info("Clicking specifications button...")
            await specs_button.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            await specs_button.click()
            
            # Wait for the slide panel to open
            await asyncio.sleep(3)
            
            # Wait for the specifications panel content
            try:
                specs_panel = await self.page.wait_for_selector(
                    'div[data-testid="brix-sheet-content"]',
                    timeout=10000,
                    state="visible"
                )
            except Exception as e:
                self.logger.warning(f"Specifications panel not found for product: {product_name[:50]}... - {e}")
                return {}
            
            # Find the specifications list
            specs_list = await specs_panel.query_selector('ul')
            if not specs_list:
                self.logger.warning(f"Specifications list not found for product: {product_name[:50]}...")
                return {}
            
            # Get all specification items
            spec_items = await specs_list.query_selector_all('li')
            self.logger.info(f"Found {len(spec_items)} specification items")
            
            specs = {}
            
            for i, item in enumerate(spec_items):
                try:
                    # Find the div containing the spec name and value
                    spec_div = await item.query_selector('div.dB7j8sHUbncyf79K')
                    if not spec_div:
                        # Try alternative selectors for the specification container
                        alternative_selectors = [
                            'div[class*="inline-flex"][class*="w-full"]',
                            'div.inline-flex.w-full',
                            'div:has(div.grow)'
                        ]
                        for alt_selector in alternative_selectors:
                            spec_div = await item.query_selector(alt_selector)
                            if spec_div:
                                break
                    
                    if spec_div:
                        # Get the two divs containing spec name and value
                        spec_divs = await spec_div.query_selector_all('div.grow')
                        
                        if len(spec_divs) >= 2:
                            spec_name_elem = spec_divs[0]
                            spec_value_elem = spec_divs[1]
                            
                            spec_name = await spec_name_elem.text_content()
                            spec_value = await spec_value_elem.text_content()
                            
                            if spec_name and spec_value:
                                # Clean and normalize the spec name for use as key
                                clean_name = spec_name.strip().lower().replace(' ', '_').replace('-', '_')
                                clean_value = spec_value.strip()
                                
                                specs[clean_name] = clean_value
                                self.logger.debug(f"Spec {i+1}: {clean_name} = {clean_value}")
                        else:
                            self.logger.debug(f"Insufficient spec divs found for item {i+1}")
                    else:
                        self.logger.debug(f"Spec container div not found for item {i+1}")
                        
                except Exception as e:
                    self.logger.warning(f"Error processing specification item {i+1}: {e}")
                    continue
            
            # Close the specifications panel (click outside or find close button)
            try:
                # Try to find and click a close button first
                close_selectors = [
                    'button[aria-label="Close"]',
                    'button[aria-label="close"]',
                    '.close-button',
                    '[data-testid*="close"]'
                ]
                
                close_button = None
                for selector in close_selectors:
                    try:
                        close_button = await self.page.query_selector(selector)
                        if close_button and await close_button.is_visible():
                            break
                    except:
                        continue
                
                if close_button:
                    await close_button.click()
                else:
                    # Click outside the panel or press Escape
                    await self.page.keyboard.press('Escape')
                
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.debug(f"Could not close specifications panel: {e}")
            
            self.logger.info(f"Successfully extracted {len(specs)} specifications for: {product_name[:50]}...")
            return specs
            
        except Exception as e:
            self.logger.error(f"Error extracting specifications for {product_name[:50]}...: {e}")
            return {}

    async def scrape_reviews_from_current_page(self) -> List[Dict]:
        """
        Scrape reviews from the current reviews page.
        
        Returns:
            List of review dictionaries from the current page
        """
        try:
            # Wait for reviews list to be available
            reviews_list = await self.page.wait_for_selector('ul.reviews-list', timeout=5000)
            
            if not reviews_list:
                return []
            
            # Get all review items on current page
            review_items = await reviews_list.query_selector_all('li.review-item')
            
            reviews = []
            
            for i, item in enumerate(review_items):
                try:
                    review_data = {
                        "title": "",
                        "description": ""
                    }
                    
                    # Extract review title
                    try:
                        title_element = await item.query_selector('h4.review-title')
                        if title_element:
                            title_text = await title_element.text_content()
                            if title_text:
                                review_data["title"] = title_text.strip()
                    except Exception as e:
                        self.logger.debug(f"Could not extract title for review {i+1}: {e}")
                    
                    # Extract review description
                    try:
                        description_element = await item.query_selector('p.pre-white-space')
                        if description_element:
                            description_text = await description_element.text_content()
                            if description_text:
                                review_data["description"] = description_text.strip()
                    except Exception as e:
                        self.logger.debug(f"Could not extract description for review {i+1}: {e}")
                    
                    # Add review if we have at least title or description
                    if review_data["title"] or review_data["description"]:
                        reviews.append(review_data)
                        self.logger.debug(f"Review {i+1}: {review_data['title'][:30]}...")
                    
                except Exception as e:
                    self.logger.warning(f"Error processing review {i+1}: {e}")
                    continue
            
            return reviews
            
        except Exception as e:
            self.logger.error(f"Error scraping reviews from current page: {e}")
            return []

    async def find_next_page_button(self) -> Optional[object]:
        """
        Find the next page button in pagination.
        
        Returns:
            The next page button element if found, None otherwise
        """
        try:
            # Look for next page button with various selectors
            next_button_selectors = [
                'li.page.next',
                'li.page.next a',
                'li.page.next button',
                '.page.next',
                '.page.next a',
                '.page.next button',
                'a[aria-label*="Next"]',
                'button[aria-label*="Next"]',
                '.pagination li.next',
                '.pagination li.next a',
                '.pagination .next',
                'li[class*="page"][class*="next"]',
                'li[class*="next"] a',
                'li[class*="next"] button'
            ]
            
            for selector in next_button_selectors:
                try:
                    next_button = await self.page.query_selector(selector)
                    if next_button and await next_button.is_visible():
                        # Check if the button is not disabled
                        is_disabled = await next_button.get_attribute('disabled')
                        aria_disabled = await next_button.get_attribute('aria-disabled')
                        classes = await next_button.get_attribute('class') or ''
                        
                        if (is_disabled != 'true' and 
                            aria_disabled != 'true' and 
                            'disabled' not in classes.lower()):
                            
                            self.logger.debug(f"Found next page button with selector: {selector}")
                            return next_button
                        else:
                            self.logger.debug(f"Next button found but disabled with selector: {selector}")
                            
                except Exception as e:
                    self.logger.debug(f"Next button selector {selector} failed: {e}")
                    continue
            
            # If not found with standard selectors, try text-based search
            all_clickable = await self.page.query_selector_all('a, button, [role="button"], [role="link"]')
            for element in all_clickable:
                try:
                    text_content = await element.text_content()
                    if text_content and any(text in text_content.lower() for text in ['next', '>', '→']):
                        if await element.is_visible():
                            # Check if it's in a pagination context
                            parent_element = await element.query_selector('..')
                            if parent_element:
                                parent_class = await parent_element.get_attribute('class') or ''
                                if any(cls in parent_class.lower() for cls in ['page', 'pagination', 'next']):
                                    self.logger.debug(f"Found next button by text search: {text_content.strip()}")
                                    return element
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding next page button: {e}")
            return None

    async def scrape_all_product_reviews_concurrent(self, max_concurrent_tabs: int = 4) -> List[Dict]:
        """
        Load products from JSON file and scrape specifications and reviews for each product using concurrent processing.
        
        Args:
            max_concurrent_tabs: Maximum number of concurrent browser tabs to use (default: 4)
        
        Returns:
            List of products with their specifications and reviews included
        """
        try:
            self.logger.info("=== Starting CONCURRENT product data scraping ===")
            self.logger.info(f"Using {max_concurrent_tabs} concurrent browser tabs for faster processing")
            
            # Load existing products from JSON
            products = await self.load_products_from_json("laptop_products_all_pages.json")
            
            # Create multiple browser pages for concurrent processing
            pages = []
            for i in range(max_concurrent_tabs):
                page = await self.context.new_page()
                page.set_default_timeout(config.DEFAULT_TIMEOUT)
                page.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)
                pages.append(page)
                self.logger.info(f"Created browser tab {i+1}/{max_concurrent_tabs}")
            
            # Divide products into chunks for concurrent processing
            import math
            chunk_size = math.ceil(len(products) / max_concurrent_tabs)
            product_chunks = [products[i:i + chunk_size] for i in range(0, len(products), chunk_size)]
            
            self.logger.info(f"Divided {len(products)} products into {len(product_chunks)} chunks")
            for i, chunk in enumerate(product_chunks):
                self.logger.info(f"  Chunk {i+1}: {len(chunk)} products")
            
            # Create concurrent tasks
            tasks = []
            for i, (page, chunk) in enumerate(zip(pages, product_chunks)):
                if chunk:  # Only create task if chunk has products
                    task = self.process_product_chunk(page, chunk, i+1)
                    tasks.append(task)
            
            # Execute all chunks concurrently
            self.logger.info(f"Starting concurrent processing with {len(tasks)} worker tasks...")
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results from all chunks
            all_products_with_data = []
            total_specs = 0
            total_reviews = 0
            
            for i, result in enumerate(chunk_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Chunk {i+1} failed with error: {result}")
                    continue
                elif isinstance(result, list):
                    all_products_with_data.extend(result)
                    # Count stats for this chunk
                    chunk_reviews = sum(len(product.get('reviews', [])) for product in result)
                    chunk_specs = sum(len(product.get('product_specs', {})) for product in result)
                    total_reviews += chunk_reviews
                    total_specs += chunk_specs
                    self.logger.info(f"Chunk {i+1} completed: {len(result)} products, {chunk_specs} specs, {chunk_reviews} reviews")
            
            # Close all additional browser pages
            for i, page in enumerate(pages):
                try:
                    await page.close()
                    self.logger.debug(f"Closed browser tab {i+1}")
                except Exception as e:
                    self.logger.warning(f"Error closing tab {i+1}: {e}")
            
            self.logger.info("=== CONCURRENT product data scraping completed ===")
            self.logger.info(f"Total products processed: {len(all_products_with_data)}")
            self.logger.info(f"Total specifications scraped: {total_specs}")
            self.logger.info(f"Total reviews scraped: {total_reviews}")
            
            return all_products_with_data
            
        except Exception as e:
            self.logger.error(f"Error during concurrent product data scraping: {e}")
            raise

    async def process_product_chunk(self, page: "Page", products: List[Dict], worker_id: int) -> List[Dict]:
        """
        Process a chunk of products using a dedicated browser page.
        
        Args:
            page: Browser page to use for this chunk
            products: List of products to process
            worker_id: ID of this worker for logging
            
        Returns:
            List of processed products with specifications and reviews
        """
        try:
            self.logger.info(f"Worker {worker_id}: Starting to process {len(products)} products")
            
            products_with_data = []
            
            for i, product in enumerate(products):
                try:
                    self.logger.info(f"Worker {worker_id}: Processing product {i+1}/{len(products)}: {product.get('product_name', 'Unknown')[:50]}...")
                    
                    # Skip products without URLs
                    if not product.get('url'):
                        self.logger.warning(f"Worker {worker_id}: Skipping product {i+1} - no URL available")
                        continue
                    
                    # Create enhanced product data structure
                    enhanced_product = {
                        "product_name": product.get('product_name', ''),
                        "product_price": product.get('price', ''),
                        "rating": product.get('rating', ''),
                        "number_of_reviews": product.get('number_of_reviews', ''),
                        "product_url": product.get('url', ''),
                        "product_specs": {},
                        "reviews": []
                    }
                    
                    # Scrape specifications and reviews for this product
                    product_data = await self.scrape_product_reviews_with_page(
                        page,
                        product.get('url', ''),
                        product.get('product_name', f'Product {i+1}'),
                        worker_id
                    )
                    
                    # Update the enhanced product with scraped data
                    enhanced_product["product_specs"] = product_data.get("product_specs", {})
                    enhanced_product["reviews"] = product_data.get("reviews", [])
                    
                    products_with_data.append(enhanced_product)
                    
                    # Log progress for this worker
                    specs_count = len(enhanced_product["product_specs"])
                    reviews_count = len(enhanced_product["reviews"])
                    self.logger.info(f"Worker {worker_id}: ✅ Product {i+1}: {specs_count} specs, {reviews_count} reviews")
                    
                    # Small delay between products to be respectful to the server
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Worker {worker_id}: Error processing product {i+1}: {e}")
                    # Continue with next product even if one fails
                    continue
            
            self.logger.info(f"Worker {worker_id}: Completed processing {len(products_with_data)} products successfully")
            return products_with_data
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Error processing product chunk: {e}")
            return []

    async def scrape_product_reviews_with_page(self, page: "Page", product_url: str, product_name: str, worker_id: int) -> Dict:
        """
        Navigate to a product page, scrape specifications and customer reviews using a specific browser page.
        This is the concurrent version that works with a dedicated page instead of self.page.
        
        Args:
            page: Specific browser page to use
            product_url: The URL of the product page
            product_name: Name of the product (for logging)
            worker_id: ID of the worker for logging
            
        Returns:
            Dictionary with product specs and reviews
        """
        try:
            self.logger.debug(f"Worker {worker_id}: Scraping product data for: {product_name[:50]}...")
            
            # Navigate to product page
            await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            
            # Handle country selection if it appears (using the specific page)
            await self.handle_country_selection_for_page(page, worker_id)
            
            # Handle location permission if it appears (using the specific page)
            await self.handle_location_permission_for_page(page, worker_id)
            
            # First, extract product specifications
            product_specs = await self.extract_product_specifications_for_page(page, product_name, worker_id)
            
            # Scroll down to 75% of the page to load the "See All Customer Reviews" button
            await page.evaluate("""
                const scrollHeight = document.body.scrollHeight;
                const scrollTo = scrollHeight * 0.75;
                window.scrollTo({
                    top: scrollTo,
                    behavior: 'smooth'
                });
            """)
            
            # Wait 5 seconds for the button to load (reduced from 10 for speed)
            await asyncio.sleep(5)
            
            # Wait for network activity to settle
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass  # Continue if network doesn't idle quickly
            
            # Look for "See All Customer Reviews" button
            review_button_selectors = [
                'button:has-text("See All Customer Reviews")',
                'button[aria-label*="See All Customer Reviews"]',
                'a:has-text("See All Customer Reviews")',
                'button.relative.border-xs:has-text("See All Customer Reviews")',
                '[role="link"]:has-text("See All Customer Reviews")',
                'button[class*="relative"][class*="border"]:has-text("See All Customer Reviews")',
                '[class*="Op9coqeII1kYHR9Q"]:has-text("See All Customer Reviews")',
                'button:text("See All Customer Reviews")',
                'a:text("See All Customer Reviews")'
            ]
            
            review_button = None
            for selector in review_button_selectors:
                try:
                    review_button = await page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state="visible"
                    )
                    if review_button:
                        break
                except Exception as e:
                    self.logger.debug(f"Review button selector {selector} failed: {e}")
                    continue
            
            # If button not found, try searching for it in the entire page
            if not review_button:
                all_buttons = await page.query_selector_all('button, a, [role="button"], [role="link"]')
                for button in all_buttons:
                    try:
                        text_content = await button.text_content()
                        if text_content and "See All Customer Reviews" in text_content:
                            if await button.is_visible():
                                review_button = button
                                break
                    except Exception:
                        continue
            
            if not review_button:
                self.logger.warning(f"Worker {worker_id}: Reviews button not found for product: {product_name[:50]}...")
                # Return with specs but no reviews
                return {
                    "product_specs": product_specs,
                    "reviews": []
                }
            
            # Click the reviews button
            await review_button.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            await review_button.click()
            
            # Wait for reviews page to load
            await asyncio.sleep(3)
            await page.wait_for_load_state("domcontentloaded")
            
            # Wait for reviews list to be available
            try:
                await page.wait_for_selector('ul.reviews-list', timeout=8000, state="visible")
            except Exception:
                self.logger.warning(f"Worker {worker_id}: Reviews list not found for product: {product_name[:50]}...")
                return {
                    "product_specs": product_specs,
                    "reviews": []
                }
            
            # Scrape reviews from all pages (handle pagination)
            all_reviews = []
            page_number = 1
            max_pages = 10  # Safety limit
            
            while page_number <= max_pages:
                # Get reviews from current page
                page_reviews = await self.scrape_reviews_from_current_page_for_page(page, worker_id)
                
                if page_reviews:
                    all_reviews.extend(page_reviews)
                else:
                    break
                
                # Check for next page button
                next_button = await self.find_next_page_button_for_page(page, worker_id)
                
                if next_button:
                    await next_button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await next_button.click()
                    await asyncio.sleep(2)
                    await page.wait_for_load_state("domcontentloaded")
                    
                    try:
                        await page.wait_for_selector('ul.reviews-list', timeout=3000)
                    except Exception:
                        break
                    
                    page_number += 1
                else:
                    break
            
            self.logger.debug(f"Worker {worker_id}: Scraped {len(all_reviews)} reviews from {page_number} page(s)")
            
            # Return combined data
            return {
                "product_specs": product_specs,
                "reviews": all_reviews
            }
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Error scraping product data: {e}")
            return {
                "product_specs": {},
                "reviews": []
            }

    async def run_review_scraping_task(self, use_concurrent: bool = True, max_concurrent_tabs: int = 4) -> dict:
        """
        Execute the comprehensive product data scraping task (specifications and reviews) for all products.
        
        Args:
            use_concurrent: Whether to use concurrent processing (default: True)
            max_concurrent_tabs: Maximum number of concurrent browser tabs (default: 4)
            
        Returns:
            Summary information dictionary
        """
        try:
            mode = "CONCURRENT" if use_concurrent else "SEQUENTIAL"
            self.logger.info(f"=== Starting Product Data Scraping Task ({mode}) ===")
            
            # Launch browser
            await self.launch_browser()
            
            # Choose processing method
            if use_concurrent:
                self.logger.info(f"Using concurrent processing with {max_concurrent_tabs} browser tabs")
                products_with_data = await self.scrape_all_product_reviews_concurrent(max_concurrent_tabs)
            else:
                self.logger.info("Using sequential processing")
                products_with_data = await self.scrape_all_product_reviews()
            
            # Save enhanced products with specifications and reviews to JSON file
            await self.save_products_to_json(products_with_data, "laptop_products_with_specs_and_reviews.json")
            
            # Take final screenshot
            await self.take_screenshot("product_data_scraping_completed.png")
            
            # Calculate summary statistics
            total_products = len(products_with_data)
            total_reviews = sum(len(product.get('reviews', [])) for product in products_with_data)
            total_specs = sum(len(product.get('product_specs', {})) for product in products_with_data)
            products_with_reviews_count = sum(1 for product in products_with_data if len(product.get('reviews', [])) > 0)
            products_with_specs_count = sum(1 for product in products_with_data if len(product.get('product_specs', {})) > 0)
            
            summary = {
                "task": "product_data_scraping",
                "processing_mode": mode.lower(),
                "concurrent_tabs_used": max_concurrent_tabs if use_concurrent else 1,
                "total_products_processed": total_products,
                "products_with_specs": products_with_specs_count,
                "products_with_reviews": products_with_reviews_count,
                "total_specifications_scraped": total_specs,
                "total_reviews_scraped": total_reviews,
                "average_specs_per_product": round(total_specs / max(total_products, 1), 2),
                "average_reviews_per_product": round(total_reviews / max(total_products, 1), 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.logger.info(f"=== Product Data Scraping Task ({mode}) completed successfully ===")
            self.logger.info(f"Summary: {summary}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Product data scraping task failed: {e}")
            raise
        finally:
            await self.cleanup()

    async def handle_country_selection_for_page(self, page: "Page", worker_id: int) -> None:
        """
        Handle the country selection screen if it appears for a specific page.
        """
        try:
            # Check if the country selection screen is present
            country_selection_header = await page.query_selector('h1:has-text("Choose a country.")')
            
            if country_selection_header:
                self.logger.info(f"Worker {worker_id}: Country selection screen detected")
                
                # Look for the United States option
                us_option = await page.query_selector('h4:has-text("United States")')
                
                if us_option:
                    self.logger.info(f"Worker {worker_id}: Clicking on United States option...")
                    await us_option.click()
                    await page.wait_for_load_state("domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
                    await asyncio.sleep(2)
                else:
                    self.logger.warning(f"Worker {worker_id}: United States option not found")
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Error handling country selection: {e}")

    async def handle_location_permission_for_page(self, page: "Page", worker_id: int) -> None:
        """
        Handle location permission alert/dialog if it appears for a specific page.
        """
        try:
            # Grant geolocation permission at page level
            await page.context.grant_permissions(['geolocation'])
            
            # Set up dialog handler for browser-level dialogs
            async def dialog_handler(dialog):
                self.logger.debug(f"Worker {worker_id}: Dialog detected: {dialog.type} - {dialog.message}")
                try:
                    await dialog.accept()
                except Exception as e:
                    self.logger.debug(f"Worker {worker_id}: Error handling dialog: {e}")
            
            # Add dialog listener
            page.on("dialog", dialog_handler)
            
            # Wait for potential dialogs and page popups
            await asyncio.sleep(1)
            
            # Check for common location permission selectors
            location_selectors = [
                'button:has-text("Allow")',
                'button:has-text("Block")',
                'button:has-text("Not now")',
                'button:has-text("Later")',
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
                'button[aria-label="Close"]'
            ]
            
            for selector in location_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            text_content = await element.text_content() or ""
                            if any(keyword in text_content.lower() for keyword in ['allow', 'block', 'not now', 'later', 'dismiss', 'close']):
                                await element.click()
                                await asyncio.sleep(1)
                                break
                except Exception:
                    continue
            
            # Try pressing Escape key to dismiss overlays
            await page.keyboard.press('Escape')
            await asyncio.sleep(0.5)
            
            # Remove dialog listener
            page.remove_listener("dialog", dialog_handler)
            
        except Exception as e:
            self.logger.debug(f"Worker {worker_id}: Error handling location permission: {e}")

    async def extract_product_specifications_for_page(self, page: "Page", product_name: str, worker_id: int) -> Dict:
        """
        Extract product specifications by clicking the specifications button for a specific page.
        """
        try:
            # Look for the specifications button using data-testid
            specs_button_selectors = [
                'button[data-testid="brix-button"]',
                'button[data-testid="brix-button"]:has-text("Specifications")',
                'button.c-button-unstyled[data-testid="brix-button"]'
            ]
            
            specs_button = None
            for selector in specs_button_selectors:
                try:
                    specs_button = await page.wait_for_selector(selector, timeout=3000, state="visible")
                    if specs_button:
                        # Check if this button contains "Specifications" text
                        button_text = await specs_button.text_content()
                        if button_text and "Specifications" in button_text:
                            break
                        else:
                            specs_button = None
                except Exception:
                    continue
            
            if not specs_button:
                self.logger.warning(f"Worker {worker_id}: Specifications button not found for: {product_name[:50]}...")
                return {}
            
            # Click the specifications button
            await specs_button.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await specs_button.click()
            await asyncio.sleep(2)
            
            # Wait for the specifications panel content
            try:
                specs_panel = await page.wait_for_selector('div[data-testid="brix-sheet-content"]', timeout=5000, state="visible")
            except Exception:
                self.logger.warning(f"Worker {worker_id}: Specifications panel not found for: {product_name[:50]}...")
                return {}
            
            # Find the specifications list
            specs_list = await specs_panel.query_selector('ul')
            if not specs_list:
                return {}
            
            # Get all specification items
            spec_items = await specs_list.query_selector_all('li')
            specs = {}
            
            for item in spec_items:
                try:
                    # Find the div containing the spec name and value
                    spec_div = await item.query_selector('div.dB7j8sHUbncyf79K')
                    if not spec_div:
                        # Try alternative selectors
                        alternative_selectors = [
                            'div[class*="inline-flex"][class*="w-full"]',
                            'div.inline-flex.w-full',
                            'div:has(div.grow)'
                        ]
                        for alt_selector in alternative_selectors:
                            spec_div = await item.query_selector(alt_selector)
                            if spec_div:
                                break
                    
                    if spec_div:
                        # Get the two divs containing spec name and value
                        spec_divs = await spec_div.query_selector_all('div.grow')
                        
                        if len(spec_divs) >= 2:
                            spec_name = await spec_divs[0].text_content()
                            spec_value = await spec_divs[1].text_content()
                            
                            if spec_name and spec_value:
                                clean_name = spec_name.strip().lower().replace(' ', '_').replace('-', '_')
                                clean_value = spec_value.strip()
                                specs[clean_name] = clean_value
                                
                except Exception:
                    continue
            
            # Close the specifications panel
            try:
                await page.keyboard.press('Escape')
                await asyncio.sleep(1)
            except Exception:
                pass
            
            self.logger.debug(f"Worker {worker_id}: Extracted {len(specs)} specifications")
            return specs
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Error extracting specifications: {e}")
            return {}

    async def scrape_reviews_from_current_page_for_page(self, page: "Page", worker_id: int) -> List[Dict]:
        """
        Scrape reviews from the current reviews page for a specific page.
        """
        try:
            # Wait for reviews list to be available
            reviews_list = await page.wait_for_selector('ul.reviews-list', timeout=3000)
            
            if not reviews_list:
                return []
            
            # Get all review items on current page
            review_items = await reviews_list.query_selector_all('li.review-item')
            reviews = []
            
            for item in review_items:
                try:
                    review_data = {"title": "", "description": ""}
                    
                    # Extract review title
                    try:
                        title_element = await item.query_selector('h4.review-title')
                        if title_element:
                            title_text = await title_element.text_content()
                            if title_text:
                                review_data["title"] = title_text.strip()
                    except Exception:
                        pass
                    
                    # Extract review description
                    try:
                        description_element = await item.query_selector('p.pre-white-space')
                        if description_element:
                            description_text = await description_element.text_content()
                            if description_text:
                                review_data["description"] = description_text.strip()
                    except Exception:
                        pass
                    
                    # Add review if we have at least title or description
                    if review_data["title"] or review_data["description"]:
                        reviews.append(review_data)
                    
                except Exception:
                    continue
            
            return reviews
            
        except Exception:
            return []

    async def find_next_page_button_for_page(self, page: "Page", worker_id: int) -> Optional[object]:
        """
        Find the next page button in pagination for a specific page.
        """
        try:
            # Look for next page button with various selectors
            next_button_selectors = [
                'li.page.next',
                'li.page.next a',
                'li.page.next button',
                '.page.next',
                '.page.next a',
                '.page.next button',
                'a[aria-label*="Next"]',
                'button[aria-label*="Next"]'
            ]
            
            for selector in next_button_selectors:
                try:
                    next_button = await page.query_selector(selector)
                    if next_button and await next_button.is_visible():
                        # Check if the button is not disabled
                        is_disabled = await next_button.get_attribute('disabled')
                        aria_disabled = await next_button.get_attribute('aria-disabled')
                        classes = await next_button.get_attribute('class') or ''
                        
                        if (is_disabled != 'true' and 
                            aria_disabled != 'true' and 
                            'disabled' not in classes.lower()):
                            return next_button
                            
                except Exception:
                    continue
            
            return None
            
        except Exception:
            return None

    async def scrape_all_product_reviews(self) -> List[Dict]:
        """
        Load products from JSON file and scrape specifications and reviews for each product.
        This is the original sequential version - kept for backwards compatibility.
        
        Returns:
            List of products with their specifications and reviews included
        """
        try:
            self.logger.info("=== Starting comprehensive product data scraping ===")
            
            # Load existing products from JSON
            products = await self.load_products_from_json("laptop_products_all_pages.json")
            
            products_with_data = []
            total_products = len(products)
            
            for i, product in enumerate(products):
                try:
                    self.logger.info(f"Processing product {i+1}/{total_products}: {product.get('product_name', 'Unknown')[:50]}...")
                    
                    # Skip products without URLs
                    if not product.get('url'):
                        self.logger.warning(f"Skipping product {i+1} - no URL available")
                        continue
                    
                    # Create enhanced product data structure
                    enhanced_product = {
                        "product_name": product.get('product_name', ''),
                        "product_price": product.get('price', ''),
                        "rating": product.get('rating', ''),
                        "number_of_reviews": product.get('number_of_reviews', ''),
                        "product_url": product.get('url', ''),
                        "product_specs": {},
                        "reviews": []
                    }
                    
                    # Scrape specifications and reviews for this product
                    product_data = await self.scrape_product_reviews(
                        product.get('url', ''),
                        product.get('product_name', f'Product {i+1}')
                    )
                    
                    # Update the enhanced product with scraped data
                    enhanced_product["product_specs"] = product_data.get("product_specs", {})
                    enhanced_product["reviews"] = product_data.get("reviews", [])
                    
                    products_with_data.append(enhanced_product)
                    
                    # Log progress
                    specs_count = len(enhanced_product["product_specs"])
                    reviews_count = len(enhanced_product["reviews"])
                    self.logger.info(f"✅ Product {i+1}: {specs_count} specs, {reviews_count} reviews")
                    
                    # Take screenshot for verification (optional, every 10th product)
                    if i % 10 == 0:
                        await self.take_screenshot(f"data_scraping_product_{i+1:03d}.png")
                    
                    # Small delay between products to be respectful
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing product {i+1}: {e}")
                    # Continue with next product even if one fails
                    continue
            
            self.logger.info("=== Product data scraping completed ===")
            self.logger.info(f"Total products processed: {len(products_with_data)}")
            
            # Calculate total reviews and specs scraped
            total_reviews = sum(len(product.get('reviews', [])) for product in products_with_data)
            total_specs = sum(len(product.get('product_specs', {})) for product in products_with_data)
            self.logger.info(f"Total specifications scraped: {total_specs}")
            self.logger.info(f"Total reviews scraped: {total_reviews}")
            
            return products_with_data
            
        except Exception as e:
            self.logger.error(f"Error during comprehensive product data scraping: {e}")
            raise

    async def scrape_product_subset_concurrent(self, products_subset: List[Dict], max_concurrent_tabs: int = 4) -> List[Dict]:
        """
        Scrape specifications and reviews for a specific subset of products using concurrent processing.
        This is useful for testing with a smaller number of products.
        
        Args:
            products_subset: List of products to process
            max_concurrent_tabs: Maximum number of concurrent browser tabs to use (default: 4)
        
        Returns:
            List of products with their specifications and reviews included
        """
        try:
            self.logger.info(f"=== Starting CONCURRENT subset scraping for {len(products_subset)} products ===")
            self.logger.info(f"Using {max_concurrent_tabs} concurrent browser tabs for faster processing")
            
            # Create multiple browser pages for concurrent processing
            pages = []
            for i in range(max_concurrent_tabs):
                page = await self.context.new_page()
                page.set_default_timeout(config.DEFAULT_TIMEOUT)
                page.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)
                pages.append(page)
                self.logger.info(f"Created browser tab {i+1}/{max_concurrent_tabs}")
            
            # Divide products into chunks for concurrent processing
            import math
            chunk_size = math.ceil(len(products_subset) / max_concurrent_tabs)
            product_chunks = [products_subset[i:i + chunk_size] for i in range(0, len(products_subset), chunk_size)]
            
            self.logger.info(f"Divided {len(products_subset)} products into {len(product_chunks)} chunks")
            for i, chunk in enumerate(product_chunks):
                self.logger.info(f"  Chunk {i+1}: {len(chunk)} products")
            
            # Create concurrent tasks
            tasks = []
            for i, (page, chunk) in enumerate(zip(pages, product_chunks)):
                if chunk:  # Only create task if chunk has products
                    task = self.process_product_chunk(page, chunk, i+1)
                    tasks.append(task)
            
            # Execute all chunks concurrently
            self.logger.info(f"Starting concurrent processing with {len(tasks)} worker tasks...")
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results from all chunks
            all_products_with_data = []
            total_specs = 0
            total_reviews = 0
            
            for i, result in enumerate(chunk_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Chunk {i+1} failed with error: {result}")
                    continue
                elif isinstance(result, list):
                    all_products_with_data.extend(result)
                    # Count stats for this chunk
                    chunk_reviews = sum(len(product.get('reviews', [])) for product in result)
                    chunk_specs = sum(len(product.get('product_specs', {})) for product in result)
                    total_reviews += chunk_reviews
                    total_specs += chunk_specs
                    self.logger.info(f"Chunk {i+1} completed: {len(result)} products, {chunk_specs} specs, {chunk_reviews} reviews")
            
            # Close all additional browser pages
            for i, page in enumerate(pages):
                try:
                    await page.close()
                    self.logger.debug(f"Closed browser tab {i+1}")
                except Exception as e:
                    self.logger.warning(f"Error closing tab {i+1}: {e}")
            
            self.logger.info("=== CONCURRENT subset scraping completed ===")
            self.logger.info(f"Total products processed: {len(all_products_with_data)}")
            self.logger.info(f"Total specifications scraped: {total_specs}")
            self.logger.info(f"Total reviews scraped: {total_reviews}")
            
            return all_products_with_data
            
        except Exception as e:
            self.logger.error(f"Error during concurrent subset scraping: {e}")
            raise


async def main():
    """Main entry point for the automation script."""
    automation = BestBuyAutomation()
    
    # Check if we should run review scraping task
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reviews":
        try:
            # Parse additional arguments for concurrent processing
            use_concurrent = True
            max_concurrent_tabs = 4
            
            # Check for --sequential flag
            if "--sequential" in sys.argv:
                use_concurrent = False
                print("🔄 Using SEQUENTIAL processing mode")
            else:
                print("🚀 Using CONCURRENT processing mode (default)")
            
            # Check for --tabs argument
            if "--tabs" in sys.argv:
                try:
                    tabs_index = sys.argv.index("--tabs") + 1
                    if tabs_index < len(sys.argv):
                        max_concurrent_tabs = int(sys.argv[tabs_index])
                        print(f"🔧 Using {max_concurrent_tabs} concurrent tabs")
                except (ValueError, IndexError):
                    print("⚠️ Invalid --tabs argument, using default: 4")
                    max_concurrent_tabs = 4
            
            result = await automation.run_review_scraping_task(use_concurrent, max_concurrent_tabs)
            print(f"Product data scraping task completed successfully!")
            print(f"Processing mode: {result.get('processing_mode', 'N/A').upper()}")
            print(f"Concurrent tabs used: {result.get('concurrent_tabs_used', 'N/A')}")
            print(f"Total products processed: {result.get('total_products_processed', 'N/A')}")
            print(f"Products with specifications: {result.get('products_with_specs', 'N/A')}")
            print(f"Products with reviews: {result.get('products_with_reviews', 'N/A')}")
            print(f"Total specifications scraped: {result.get('total_specifications_scraped', 'N/A')}")
            print(f"Total reviews scraped: {result.get('total_reviews_scraped', 'N/A')}")
            print(f"Average specs per product: {result.get('average_specs_per_product', 'N/A')}")
            print(f"Average reviews per product: {result.get('average_reviews_per_product', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            
        except Exception as e:
            print(f"Product data scraping task failed: {e}")
            return 1
    else:
        # Run the original product listing scraping task
        try:
            result = await automation.run_task_1()
            print(f"Task 1 completed successfully!")
            print(f"Page URL: {result.get('url', 'N/A')}")
            print(f"Page Title: {result.get('title', 'N/A')}")
            print(f"Products scraped: {result.get('products_scraped', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            
        except Exception as e:
            print(f"Task 1 failed: {e}")
            return 1
        
    return 0


if __name__ == "__main__":
    # Run the automation
    exit_code = asyncio.run(main())
    exit(exit_code) 